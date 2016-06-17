# Fantasy SSBM
Fantasy SSBM is a website that enables the creation/management of Melee fantasy leagues. Additionally, it tracks players' performances at major tournaments and then ranks those players (through use of a carefully designed rating system). To see all this and more, check out the link in the description above! 

As Charlie Puth might say, you're only one click away. :)

## Getting Started
#### Dependencies
Install pip (`sudo easy_install pip`) and virtualenv (`pip install virtualenv`). You'll need pip to install package dependencies and virtualenv to create an isolated environment for them.

Next, grab the project files and `cd` to the top level directory:
```
git clone https://github.com/ohjay/fantasy-ssbm.git
cd fantasy-ssbm
```

Finally, start a virtual environment and install the packages in `requirements.txt`:
```
virtualenv -p python2.7 venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Database Configuration
Fantasy SSBM uses Postgres both locally and in production. If you don't have Postgres installed, you can download it [here](http://www.postgresql.org/).

Once you've done that, open the Postgres app and enter the shell (by clicking "Open psql"). Then create a user and a database:
```
CREATE USER fs WITH PASSWORD 'owenrocks';
CREATE DATABASE fantasy;
GRANT ALL PRIVILEGES ON DATABASE fantasy to fs;
```

At this point, you should type `\q` to quit the Postgres shell.

#### Hidden Settings
In the interest of security, I've made sure to hide critical information when pushing to GitHub. Specifically, I've omitted `SECRET_KEY`, `AWS_SECRET_ACCESS_KEY`, and `EMAIL_HOST_PASSWORD` from `website/settings.py`. If Django complains, you may find it necessary to fill these with dummy values.

#### Email Verification
For verification to work, you'll have to change `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, and `DEFAULT_FROM_EMAIL` so that they reflect values belonging to an actual email account. If not using Gmail, you'll also need to edit `EMAIL_HOST`.

Secondly, in `fantasy_draft/views.py` you'll have to make two modifications. These modifications are best represented as "find and replace" commands:

| Find                                    | Replace             |
|:---------------------------------------:|:-------------------:|
| `fantasy-ssbm.elasticbeanstalk.com`     | `127.0.0.1:8000`    |
| `Fantasy SSBM <fantasy.ssbm@gmail.com>` | `<YOUR-EMAIL-HERE>` |

#### Running the Site
Ensure that Postgres is running on port 5432. Then `cd` into `website` and run `python manage.py runserver`. 

With luck, your local server should soon be up and running! When the command finishes, you can view the site by visiting `localhost:8000` in your favorite web browser.

#### Extra [fE]
To update the site on AWS, execute `eb deploy` from the root directory. This will synchronize the public website with the version in your latest commit.
