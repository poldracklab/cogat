''' script to move users from old cognitive atlas mysql to postgres db with
    schema based on a custom django users model'''
import os

import pymysql
import psycopg2

# postgres schema
# id            | integer
# password      | character varying(128)
# last_login    | timestamp with time zone
# is_superuser  | boolean
# username      | character varying(150)
# first_name    | character varying(30)
# last_name     | character varying(30)
# email         | character varying(254)
# is_staff      | boolean
# is_active     | boolean
# date_joined   | timestamp with time zone
# obfuscate     | boolean
# interest_tags | character varying(512)
# old_id        | character varying(36)

# mysql schema
# id                    | varchar(36)
# user_first_name       | varchar(255)
# user_last_name        | varchar(255)
# user_rank             | varchar(10)
# user_full_name        | varchar(255)
# user_honorific_prefix | varchar(255)
# user_honorific_suffix | varchar(255)
# user_org_id           | varchar(36)
# user_title            | varchar(255)
# user_interest_tags    | varchar(512)
# user_pass             | varchar(512)
# user_telephone        | varchar(255)
# user_email            | varchar(255)
# event_stamp           | timestamp
# user_gender           | varchar(255)
# user_ethnicity        | varchar(255)
# user_accepted         | varchar(50)
# user_race             | varchar(255)
# user_specialist_tags  | varchar(2000)
# user_obfuscate        | varchar(255)
# user_handle           | varchar(255)

# add title, and specialist tags

def user_imports():
    post_conn = psycopg2.connect(
        dbname=os.environ.get('POSTGRES_NAME'),
        user=os.environ.get('POSTGRES_USER'),
        password=os.environ('POSTGRES_PASS'),
        host=os.environ('POSTGRES_HOST')
    )
    post_cur = post_conn.cursor()

    my_conn = pymysql.connect(db='cogat', user='root')
    my_cur = my_conn.cursor()

    select_query = '''select id, user_first_name, user_last_name, user_interest_tags,
               user_pass, user_email, user_accepted, user_obfuscate, title, specialist_tags
               FROM table_user'''

    insert_query = '''INSERT INTO users_user (password, email, is_active,
                      obfuscate, interest_tags, old_id, title, specialist_tags, first_name, last_name)
                      VALUES({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {})'''

    old_user_lookup = "SELECT old_id from users_user where old_id='{}'"

    my_cur.execute(select_query)
    old_users = my_cur.fetchall()
    for old_user in old_users:
        post_cur.execute(old_user_lookup.format(old_user[0]))
        if not post_cur.fetch_one():
            new_user = insert_query.format(
                old_user[4],
                old_user[5],
                old_user[6],
                old_user[7],
                old_user[3],
                old_user[0],
                old_user[8],
                old_user[9],
                old_user[1],
                old_user[2]
            )
            print(new_user)
            #post_cur.execute(new_user)
            #post_cur.commit()

if __name__ == '__main__':
    user_imports()
