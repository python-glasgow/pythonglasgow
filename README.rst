Python Glasgow
==============

This is the code for www.pythonglasgow.org

The site is hosted on Heroku and uses Flask.


Setup Instructions
==================

To setup and start the website locally, use the following commands. This
assumes you are using virtualenv wrapper, if you need other help then
get in touch with @d0ugal

    mkvirtualenv pythonglasgow
    pip install -r requirements/dev.txt
    honcho start

If that all worked, you should be able to head to http://localhost:5000/

Note that some features (namely Twitter) wont work unless you can
provide API access keys.