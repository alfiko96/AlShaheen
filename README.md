A web application for Al Shaheen Recreational Club in Qatar

First component : login/register
Three HTML pages were made named login, register and forgot password which use
post method to sent the information from the web page into the python flask code.
Existing member can log in to view and gain full access to the application using an
SQL query with the correct username and password. New members have to sign up with
their email and later inserted into users table under the Al Shaheen database. Existing
members can change their password if they couldn't recall it by updating the password
using an SQL query with the correct username.

Second component: profile
An HTML page were made named profile. After successfully logging in, the user will be able to
see profile mentioning his/her first name, last name and email with the help of SQL query.
The user can also update his/her profile by simply clicking the update button where
it will take them into separate page to fill in forms according to their liking.

Third componennt: join/unjoin tournament
Two HTML pages were made named login, register and forgot password which use
post method to sent the information from the web page into the python flask code.
Four tables were created under the Al Shaheen database and they were named badminton,
basketball, tennis and volleyball. Members can participate in the categories of the
tournaments of their choosing, for example basketball, volleyball, tennis and badminton.
By clicking on the join button, the user will choose the category and select 1 participant.
There are steps to this:
- the application will ask if the participant already exists for a particular tournament
  using an SQL query
- if not, insert a new entry in the respective category of tournament
- if yes, return apology
- update the number of participants category by 1

For the unjoin part, these are the steps:
- the application will ask if the participant exists for a particular tournament
  using an SQL query
- if yes, remove the participant for the list of participants
- if no, return apology
- reduce the number of participants of the selected category by 1

Fourth part: book/unbook
Three HTML pages were made named book, and history which use post method to sent
the information from the web page into the python flask code.

There are steps to this for the book part:
- the application will ask if the booking already exists using an SQL query
- in the booking table under Al Shaheen database
- the application will ask the if the booking exceeds the one hour
- limit for one booking
- the application will ask if the total amount of bookings exceeds the two
- hour limit for a day
- if not, insert a new entry in the booking table
- if yes, return apology

For the unbook part, these are the steps:
- the application will ask if the booking exists
  using an SQL query
- if yes, remove the participant for the list of participants
- if no, return apology

The history page only displays the confirmed bookings from the book table.