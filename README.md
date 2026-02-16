# Focus Flow
#### Video Demo:  <URL HERE>
#### Description:
**Focus Flow** is a gamified Pomodoro timer that is designed to help users with their time management to stay productive by turning their _focus_ time into a _"currency"_ (XP).  The idea came from making a timer for productivity tasks, but less boring and more rewarding than a standard timer.  Some of my friends use Pomodoro timers within their workflows, those timers are just timers and have nothing special about them.  I thought it would be a cool idea to gamify a Pomodoro timer giving users reasons to actually use and implement them within their workflows.

#### How it Works:
Users will be prompted to either log in or register a profile.  Upon a successful login, the user will be welcomed to the timer page.

I chose to stay true to the Pomodoro Timer and kept the duration of the timer to be 25 minutes.  The 25 minute session is the sweet spot that aligns with our natural rhythms which allows us to work at peak efficiency.  

A visual countdown timer will be visible showing the user their progress.  Once the timer runs out in a session, the user has successfully completed the session and is rewarded with _Experience Points (XP)_.  The XP is calculated and awarded in the backend once the JavaScript timer reaches zero; this prevents the user from finding exploits to cheat to get more XP.  The XP isn't just for show, users can stack up their XP and spend it within the **Focus Shop**.

I also added a notes feature, allowing the user to type in some optional notes about what the next session is about.  During testing I found that tracking the history would be pointless if the user does not know what they accomplished in each session.  The notes are visible on the **History** page that is used for tracking past sessions, which shows the date, notes and XP gained.

#### The Shop and Theme systems:
The core feature of this project is the shop.  The shop has a few themes that the users can purchase and equip for different visual styles.

- Classic Focus: The default navy and crimson theme.
- Crimson Night: A black and deep red theme.
- Midnight Forest: A deep blue and dark green theme.
- Golden Hour: A deep blue and gold theme.
- Neon Nebula: A contrasty purple theme.

Each theme costs a different amount of XP.  Once a user buys a theme, it is saved to their account within the database.  When a theme is equiped, the sites CSS dynamically updates all the pages using a session-based class system.  When a user logs out and logs back in, their previously equiped theme will be applied.

#### Files and Project Structure
- **app.py**: This is the brain of the project, handling all the routing, authentications, XP Calculations, the logic for buying and equiping themes and updating databases.

- **focus.db**:  The SQLite database that stores user credentials, XP balances, timer history, themes and unlocked themes.

- **static/style.css**: Manages the styling for all the pages and contains the class overrides for the theme system.

- **static/script.js**: Handles the front end timer logic.  It manages the countdown intervals, updates the timer display in real time, sends data back to the server once a session has completed to trigger the XP rewards.

- **templates/layout.html**: Contains the navigation bar and uses Jinja2 to dynamically apply theme classes to the body tags.

- **templates/index.html**: The homepage featuring the timer, notes input and XP display.

- **templates/store.html**: The Focus Shop page.  It uses a 3 column grid to display the themes and handles the logic for "Buy", "Equip" and "Active" button states.

- **templates/history.html**: The History page that displays a log of the users completed sessions, included the optional notes, timestamp and XP gained.

- **templates/login.html & templates/register.html**: The authentication pages that allow users to create accounts and securely access their timer, session history, XP gained and theme inventory.

#### Database Schema:
The _focus.db_ database is a relational SQLite database consisting of four main tables that manage user data, session history and the shop system.

- **_users_**: This is the core table storing user credentials, including a unique _username_, a _hash_ (password hash), _xp_ balance and the _active theme_.

- **_sessions_**: Manages and stores the history of a users completed sessions using *user_id* as a foreign key to link back to the _users_ database.  It records the _minutes_, optional _notes_ and the _timestamp_ of when it was completed.

- **_items_**: This is the shops inventory.  It stores _name_, _type_, _price_ in XP and a _description_ that is visible in the focus shop.

- **_purchases_**: This is a table that uses a **Many-to-Many** relationship between _users_ and _items_.  By storing *user_id* and *item_id* together, the ownership of the item to the user can be verified, thus allowing the user to equip the item (theme).  This also ensures that if a user purchases an item, that item remains permanently unlocked for that users account.

#### Design Choices:
One of the challenges I had was the shop grid.  I decided to use CSS Grid with _grid-auto-rows: 1fr_ and _Flexbox_ for the cards.  This was to make sure that even if the descriptions were different lengths, the buttons would always line up perfectly at the bottom of each box.  I also chose to use **inline styles** for some specific button states to make sure any global CSS changes on other pages wouldn't break it.

Beyond the Shop Grid, I had to figure out how to handle the active state of a theme.  Initially I thought about updating the database every time the user changed the theme, but realized the _flask session_ object would be much faster.  By storing the active theme in the session, the CSS is applied instantly to all pages without needing to query the database.

#### Requirements:
This project uses:
- _Python_: The core language used for backend logic and sever-side operations.
- _Flask_: For the web framework used to handle routing, sessions and request processing.
- _Jinja2_: For dynamic templating, allowing the server to inject data/classes directly into the HTML.
- _SQLite_: For data storage.
- _CSS_: For modern styling and responsive layouts.
- _Javascript_: For the countdown timer and real-time UI updates.

#### Challenges:
One of the trickiest things I had to learn was syncing the JavaScript timer with the Flask backend.  I used the _fetch_ API to send a POST request to actually award the user with the XP only when the timer actually ran out.  Handling potential edge cases were also a challenge, ultimately I decided that the XP would only be granted if the timer fully hit zero, thus encouraging the users to fully commit to the 25 minute timer, reinforcing the core concept of the Pomodoro timer.

