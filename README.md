RASCAL: Robotic Autonomous Space Cadet Administration Lackey
============================================================

<p align="center">
  <img src="https://i.imgur.com/jmm8B6z.jpg" alt="I am RASCAL" height="250"/>
  </br>
  <sub><strong>Robotic Autonomous Space Cadet Administration Lackey</strong></sub>
</p>

---

RASCAL is a customized administration bot App for Facebook Groups, designed as a rearchitected update and expansion of [ZacSweers' Facebook Modbot](https://github.com/ZacSweers/FB_Mod_Bot). RASCAL's design is intended to aid in the speed, consistency, security, and reduction of repetitive human-led administration duties; it is **not** intended to be a replacement for administrative oversight or involvement in Facebook Groups.

RASCAL runs as a Facebook Developer App, is coded in Python 3.7 using the [facepy](https://github.com/jgorset/facepy) wrapper for Facebook Graph API, and has the following prerequisites:

- **Facebook Account for Bot:** you can set up an entirely different account for your RASCAL bot, or use your personal account if you don't require them to be separated.
- **Facebook Page for Bot:** you should create a page that will operate as the identity and administration portal and granting access tokens
- **Add Page as Group Administrator:** adding the Facebook page as an administrator for the group you want the bot to run in will allow the bot to handle assigned administrative actions
- **Register Account for Facebook Developer:** in order to sign up for Facebook Developer, you will have to go through the application process provided on the Facebook Developer website

*Why make a dedicated app instead of just creating an access token?*
Only an app (with an app ID and secret key) can programatically request an **extended** access token. Without doing this, you'd need to generate a new access token every two hours.

### RASCAL Modifications:

You may modify RASCAL to perform administrative taskmastering in individual Facebook groups, so long as RASCAL's updates and endeavors abide Asimov's Laws of Robotics:

* A robot may not injure a human being or, through inaction, allow a human being to come to harm.
* A robot must obey orders given it by human beings except where such orders would conflict with the First Law.
* A robot must protect its own existence as long as such protection does not conflict with the First or Second Law.

### RASCAL To-Do:

* Upgrade from Python 2 -> Python 3.7
* Validate facepy API Changes and Updates
* Windows / Linux Integration

* Member Management / Welcome
* Post Approval
* Administrator Protection
* Spam Post Detection / Clean-Up
* Fake Account Detection / Clean-Up
* Descriptive Comments on Images
* Interactive Replies to Comment Tags
* Database of Curated Collections Shared by Members

* Documentation

### Known Issues

* Depending on how many posts you request at once (the `LIMIT` option in FQL queries), Facebook's API periodically crashes and returns an internal server error.
  * Fortunately this doesn't seem to happen unless you ask for extremely high numbers.


**[Changelog](https://github.com/WhitneyOnTheWeb/RASCAL/blob/master/CHANGELOG.md)**