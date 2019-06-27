#!/usr/bin/env python
# coding=utf-8

import cPickle as pickle
import csv
import datetime
import getopt
import json
import os
import re
import subprocess
import sys
import time

import facepy

import facebook
import util as u
from fbxmpp import SendMsgBot
from raven import Client

'''----------------------------------------------------------------------------
Project:    RASCAL: Robotic Autonomous Space Cadet Adminstration Lackey
File:       rascal.py
Author:     @WhitneyOnTheWeb

Original:   fb_bot.py

RASCAL functional codebase for administrative tasks in Facebook Groups
----------------------------------------------------------------------------'''
__author__ = 'Whitney King'


# Method for retrieving user ID's of admins in group, ignoring bot ID
def retrieve_admin_ids(group_id, bot_id, auth_token):
    # Retrieve the uids via FQL query
    graph = facebook.GraphAPI(auth_token)
    admins_query = \
        "SELECT uid FROM group_member WHERE gid=" + group_id + " AND" + \
        " administrator AND NOT (uid = " + str(bot_id) + ")"
    admins = graph.fql(query=admins_query)

    # Parse out the uids from the response
    admins_list = [admin['uid'] for admin in admins]

    # Update the admin_ids in our properties
    saved_props = load_properties()
    saved_props['admin_ids'] = admins_list
    save_properties(saved_props)

    return admins_list


# Method for sending messages, adapted from here: http://goo.gl/oV5KtZ
def send_message(recipient, message):
    saved_props = u.load_properties()

    # Access token
    access_token = saved_props['sublets_oauth_access_token']

    # API App ID
    api_key = saved_props['sublets_api_id']

    # User ID of the bot
    botid = str(saved_props['bot_id'])

    # The "From" Facebook ID
    jid = botid + '@chat.facebook.com'

    # The "Recipient" Facebook ID, with a hyphen for some reason
    to = '-' + str(recipient) + '@chat.facebook.com'

    xmpp = SendMsgBot(jid, to, unicode(message))

    xmpp.credentials['api_key'] = api_key
    xmpp.credentials['access_token'] = access_token

    if xmpp.connect(('chat.facebook.com', 5222)):
        xmpp.process(block=True)
        log('----Message sent', Color.GREEN)
    else:
        log("----Unable to connect, message sending fail", Color.RED)


# Extracted logic for messaging admins a message
def message_admins(message, auth_token, app_id, bot_id, group_id):
    for admin in retrieve_admin_ids(group_id, bot_id, auth_token):
        send_message(str(admin), message)


# Method for checking tag validity
def check_tag_validity(message_text):
    p = re.compile(
        "^(-|\*| )*([\(\[\{])((looking)|(rooming)|(offering)|(parking))([\)\]\}])(:)?(\s|$)",
        re.IGNORECASE)

    if re.match(p, message_text):
        return True
    else:
        return False


# Method for checking if pricing reference is there
def check_price_validity(message_text):
    p = re.compile(
        "(\$)|((\d)+( )?((per)|(/)|(a))( )?(/)?((month)|(mon)|(mo))(\s)?)",
        re.IGNORECASE)

    if re.search(p, message_text) is not None:
        return True
    else:
        return False


# Checking if there's a parking tag
def check_for_parking_tag(message_text):
    p = re.compile(
        "^(-|\*| )*([\(\[\{])(parking)([\)\]\}])(:)?(\s|$)",
        re.IGNORECASE)

    if re.search(p, message_text):
        return True
    else:
        return False


# Delete posts older than 30 days old
def delete_old_posts(graph, group_id, admins):
    old_date = int(time.time()) - 2592000  # 30 days in seconds
    old_query = "SELECT post_id, message, actor_id FROM stream WHERE " + \
                "source_id=" + group_id + " AND created_time<" + str(old_date) + \
                " LIMIT 300"
    log("Getting posts older than:")
    log("\t" + datetime.datetime.fromtimestamp(old_date)
        .strftime('%Y-%m-%d %H:%M:%S'))
    posts = graph.fql(query=old_query)
    log("Deleting " + str(len(posts)) + " posts", Color.RED)
    for post in posts:
        post_id = post['post_id']
        graph.delete_object(id=post_id)

        ## Old stuff messaging users their post
        # post_message = post['message']
        # post_id = post['post_id']
        # actor_id = post['actor_id']
        #
        # if int(actor_id) not in admins:
        #     message = "We are deleting old posts. Your post's message is pasted" + \
        #         " below. Feel free to repost it if you still need to.\n\n" + \
        #               post_message
        #
        #     send_message(str(actor_id), message)
        #     log("\tDeleting " + post_id, Color.RED)
        #     graph.delete_object(id=post_id)
        #     time.sleep(2)
        # else:
        #     log("\tSkipping admin post: " + post_id, Color.BLUE)


# Main runner method
def sub_group():
    # Load the properties
    saved_props = load_properties()

    # Access token
    sublets_oauth_access_token = saved_props['sublets_oauth_access_token']

    # Access token expiration
    access_token_expiration = saved_props['access_token_expiration']

    # API App ID
    sublets_api_id = saved_props['sublets_api_id']

    # API App secret key
    sublets_secret_key = saved_props['sublets_secret_key']

    # List of posts to ignore
    ignored_post_ids = saved_props['ignored_post_ids']

    # List of people to ignore
    ignore_source_ids = saved_props['ignore_source_ids']

    # ID of the FB group
    group_id = saved_props['group_id']

    # User ID of the bot
    bot_id = saved_props['bot_id']

    # IDs of admins (unused right now, might remove later)
    admin_ids = saved_props['admin_ids']

    # Keeping track of the posts we look at here
    processed_posts = []

    # FQL query for the group
    group_query = "SELECT post_id, message, actor_id FROM stream WHERE " + \
                  "source_id=" + group_id + " LIMIT 50"

    # Get current time
    now_time = time.time()

    # For logging purposes
    log("CURRENT CST TIMESTAMP: " + datetime.datetime.fromtimestamp(
        now_time - 21600).strftime('%Y-%m-%d %H:%M:%S'), Color.UNDERLINE)

    # Make sure the access token is still valid
    if access_token_expiration < now_time:
        sys.exit("API Token is expired")

    # Warn if the token's expiring soon
    if access_token_expiration - now_time < 604800:
        log("Warning - access token expires in less than a week", Color.RED)
        log("-- Expires on " + datetime.datetime.fromtimestamp(
            access_token_expiration).strftime('%Y-%m-%d %H:%M:%S'))

        # If you want it to automatically when it's close to exp.
        global extend_key
        extend_key = True

    # Log in, try to get posts
    graph = facebook.GraphAPI(sublets_oauth_access_token)

    # Extend the access token, default is ~2 months from current date
    if extend_key:
        extend_access_token(graph, now_time, saved_props, sublets_api_id,
                            sublets_secret_key)

    # Make our first request, get the group posts
    group_posts = graph.fql(query=group_query)

    # Load the pickled cache of previously warned posts
    already_warned = dict()
    log("Loading warned cache", Color.BOLD)
    already_warned = load_cache(warned_db, already_warned)
    log('--Loading cache size: ' + str(len(already_warned)), Color.BOLD)

    # Load the pickled cache of valid posts
    valid_posts = []
    log("Checking valid cache.", Color.BOLD)
    valid_posts = load_cache(valid_db, valid_posts)
    log('--Valid cache size: ' + str(len(valid_posts)), Color.BOLD)

    # Loop over retrieved posts
    for post in group_posts:

        # Important data received
        post_message = post['message']  # Content of the post
        post_id = post['post_id']  # Unique ID of the post
        processed_posts.append(post_id)

        # Unique ID of the person that posted it
        actor_id = post['actor_id']

        # Ignore mods and certain posts
        if post_id in ignored_post_ids or actor_id in ignore_source_ids or \
                        post_id in valid_posts or int(actor_id) in admin_ids:
            # log('\n--Ignored post: ' + post_id, Color.BLUE)
            continue

        # Data to use
        post_comment = ""

        # Boolean for tracking if the post is valid
        valid_post = True

        # Counter for multiple items
        invalid_count = 0

        # Log the message details
        log("\n" + post_message[0:75].replace('\n', "") + "...\n--POST ID: " +
            str(post_id) + "\n--ACTOR ID: " + str(actor_id))

        # Check for pricing
        if not check_price_validity(post_message):
            valid_post = False
            invalid_count += 1
            post_comment += "- Please give some sort of pricing (use dollar signs!)\n"
            log('----$', Color.BLUE)

        # Check for tag validity
        if not check_tag_validity(post_message):
            valid_post = False
            invalid_count += 1
            post_comment += \
                "- You didn't include a proper tag\n"
            log('----Tag', Color.BLUE)

        # Check post length.
        # Allow short ones if there's a craigslist link or parking
        if len(post_message) < 200 and \
                        "craigslist" not in post_message.lower() \
                and not check_for_parking_tag(post_message):
            valid_post = False
            invalid_count += 1
            post_comment += \
                "- Not enough details, please give some more info\n"
            log('----Length', Color.BLUE)

        # Not a valid post
        if not valid_post:

            if invalid_count > 1:
                post_comment = "Hey buddy, your post has some issues:\n" + post_comment
            else:
                post_comment = "Hey buddy, your post has an issue:\n" + post_comment

            # If already warned, delete if it's been more than 24 hours, ignore
            # if it's been less
            if post_id in already_warned:

                # Invalid, past 24 hour grace period
                if time_limit < now_time - already_warned[post_id]:
                    log('--Delete: ' + post_id, Color.RED)
                    url = "http://www.facebook.com/" + post_id

                    # Try and delete the post with graph. If it fails, message
                    # the admins and prompt them to delete the post
                    try:
                        graph.delete_object(id=post_id)

                        log("--Confirming deletion...")
                        try:
                            # Give it a sec to propagate
                            time.sleep(3)
                            graph.get_object(id=post_id)

                            # If it got here something went wrong
                            message_admins(
                                "Please make sure this is gone: " + url,
                                sublets_oauth_access_token,
                                sublets_api_id, bot_id, group_id)
                        except:
                            log("Deletion confirmed ✓", Color.GREEN)
                            del already_warned[post_id]

                    # Something went wrong, have the admins delete it
                    except Exception as e:
                        message_admins(
                            "Delete this post: " + url,
                            sublets_oauth_access_token,
                            sublets_api_id, bot_id, group_id)
                        log(e.message + " - " + str(type(e)), Color.RED)

                # Invalid but they still have time
                else:
                    time_delta = time_limit - (now_time -
                                               already_warned[post_id])
                    m, s = divmod(time_delta, 60)
                    h, m = divmod(m, 60)
                    log_message = '--Invalid, but still have '
                    if h > 0:
                        log_message += '%d hours and ' % h
                    log_message += '%02d minutes' % m
                    log(log_message, Color.RED)
                continue

            # Comment with a warning and cache the post
            else:

                # First check to make sure we haven't warned them before
                # by searching comments for bot comment
                previously_commented = False
                comments_query = "SELECT fromid, id, time FROM comment" + \
                                 " WHERE post_id=\"" + str(post_id) + "\""
                comments = graph.fql(comments_query)
                for comment in comments:

                    # Found a comment from the bot
                    if comment['fromid'] == bot_id:
                        log('--Previously warned')
                        log('----caching')
                        previously_commented = True
                        already_warned[post_id] = comment['time']
                        break

                # Comment if no previous comment
                if not previously_commented:
                    # Comment to post for warning
                    post_comment += \
                        "\nEdit your post and fix the above within 24" + \
                        " hours, or else your post will be deleted per the" + \
                        " group rules. Thanks!"

                    graph.put_object(
                        post['post_id'], "comments", message=post_comment)
                    # Save
                    already_warned[post_id] = now_time
                    log('--WARNED', Color.RED)

        # Valid post
        else:
            log('--VALID', Color.GREEN)

            # Add to valid posts cache
            valid_posts.append(post_id)
            log('----caching', Color.GREEN)

            # Remove warning comment if it's valid now
            if post_id in already_warned:
                log('--Removing any warnings')
                comments_query = "SELECT fromid, id FROM comment" + \
                                 " WHERE post_id=\"" + str(post_id) + "\""
                comments = graph.fql(comments_query)
                for comment in comments:
                    if comment['fromid'] == int(bot_id):
                        # Delete warning comment
                        graph.delete_object(comment['id'])
                        log('--Warning deleted')

                        # Message the user notifying them the comment is deleted
                        # and thank them for fixing their post. Disabled for now
                        # log('--Thanking user')
                        # send_message(str(actor_id),
                        #              "Thanks for fixing your post," +
                        #              " I removed the warning comment.")

                # Remove post from list of warned people
                log('--Removing from cache')
                del already_warned[post_id]

    # Delete posts older than 30 days
    delete_old_posts(graph, group_id, admin_ids)

    # Keep our warned cache clean
    log('Cleaning warned posts', Color.BOLD)
    already_warned = dict((key, value) for (key, value) in
                          already_warned.items() if key in processed_posts)

    # Save the updated caches
    log('Saving warned cache', Color.BOLD)
    save_cache(warned_db, already_warned)

    log('Saving valid cache', Color.BOLD)
    save_cache(valid_db, valid_posts)

    save_properties(saved_props)

    # Done
    notify_mac()


# Main method
if __name__ == "__main__":
    # Check to see if we're running on Heroku
    if os.environ.get('MEMCACHEDCLOUD_SERVERS', None):
        import bmemcached

        log('Running on heroku, using memcached', Color.BOLD)

        # Authenticate Memcached
        running_on_heroku = True
        mc = bmemcached.Client(os.environ.get('MEMCACHEDCLOUD_SERVERS').split(','),os.environ.get('MEMCACHEDCLOUD_USERNAME'),os.environ.get('MEMCACHEDCLOUD_PASSWORD'))

    args = sys.argv
    # parser = argparse.ArgumentParser()
    # parser.add_argument("-e", help="extend the access token on run")
    # parser.add_argument("-i", help="initialize properties")
    # parser.add_argument("-t", help="only run test method")
    # parser.add_argument("-p", help="set some property values")
    # args = parser.parse_args()

    # Arg parsing. I know, there's better ways to do this
    if len(args) > 1:
        if "--extend" in args:
            extend_key = True
        elif "setprops" in args:
            set_new_props()
            sys.exit()
        elif "init" in args:
            init_props()
            sys.exit()
        elif "test" in args:
            test()
            sys.exit("Done testing")
        else:
            sys.exit('No valid args specified')

    sub_group()
    # try:
    #     sub_group()
    # except Exception:
    #     if running_on_heroku:
    #         # Use raven to capture exceptions and email
    #         # Set your raven stuff by installing it in heroku and get the python
    #         #   setup info from the Python section
    #         client = Client(os.environ.get('RAVEN'))
    #         client.captureException()
