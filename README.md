![Kaleem-logo](https://github.com/0xGhazy/0xGhazy/assets/60070427/ae61e459-47c7-4883-9002-aaf97c28fd83)

# Kaleem-Backend-APIs
Our graduation project API is an integral component of a real-time communication web app designed to empower deaf individuals by facilitating their interaction with others using sign language, which is then converted into text for non-sign language users. This innovative application tackles the challenge of bridging communication gaps and fostering inclusivity.

### Features and Functionalities:
- Logging system
- Authentication using JWT.
- Dealing with Database. you can look at external database API [here](https://github.com/kaleem-project/kaleem-database-api)
- Using SSL.
- Rate limiting.

## Requirements and Installation
to install the required libraries and dependencies use the following command

**For Linux Users**
```bash
kaleem@kali~$ pip3 isnatll -r requirements.txt
```

**For Windows Users**
```powershell
C:\> pip isnatll -r requirements.txt 
```

**Note** The `configs.json` file must be filled with your configuration:
```json
{
    "secret_key": "**********",
    "time_window_in_minuts": 43200,
    "DB_URI": "mongodb://localhost:27017",
    "DB_NAME": "database",
    "frontend_link": "http://localhost:3000",
    "mail_server_email": "**********@yahoo.com",
    "mail_server_password": "**********",
    "mail_server_host": "smtp.mail.yahoo.com",
    "mail_server_port": 465
}
```

### API Endpoints

![Kaleem API {base_url}](https://github.com/0xGhazy/PyPass/assets/60070427/b91b8d74-0708-43df-a1df-5a3aed514450)

---
### Internal Components

#### Logging system
The provided code is a Python script that implements a simple logging system. Here's an overview of what the code does:

1. It imports necessary modules including `os`, `date` and `datetime` from the `datetime` module, and `Path` from the `pathlib` module.
2. The `LogSystem` class represents the logging system. It initializes the logging directory, logging date, current time, log file name, and retrieves the list of current logs.
3. The `__create_log_file` method is a private method that checks if the log file already exists. If it doesn't exist, it calls the `write_into_log` method to write a log message indicating that the log file is created.
4. The `__get_time_now` method is a private method that retrieves the current time without the milliseconds.
5. The `write_into_log` method writes an event to the log file. It takes a `status` parameter (indicating the type of event: "+" for info, "-" for error, and "!" for warning) and a `message` parameter (containing the event message). It opens the log file in append mode and writes the event details (including status, current time, and message) to a new line in the log file.
6. The `__name__ == "__main__"` block is used to prevent the script from running when imported as a module. It creates an instance of the `LogSystem` class and calls the `write_into_log` method to write a log message indicating that the front-end application is running.

Overall, this code provides a basic logging system that writes events to a log file. It initializes the log file if it doesn't exist and allows you to write events with different statuses and messages.

```python
# code sample to add logging record to file.
log_obj = LogSystem()
log_obj.write_into_log("+", "Front-end application is running :)")
```

#### Authentication (authentication)
The provided code is a Python script that implements JWT (JSON Web Token) authentication in a Flask application. Here's an overview of what the code does:

1. It imports necessary modules including `json`, `jwt`, `wraps` from `functools`, and various modules from `flask`, `datetime`, and `pathlib`.
2. It loads the secret key from a JSON configuration file (`configs.json`) located in the parent directory of the script.
3. The `generate_jwt` function takes a secret key, a time window (in minutes), and a payload (dictionary) as input. It generates a JWT token by setting the expiration time based on the current time plus the specified time window. The payload is then encoded using the secret key and returned as a token.
4. The `decode_jwt` function takes a secret key and a JWT token as input. It decodes the token using the secret key and returns the decoded data as a dictionary.
5. The `token_required` decorator function is used to protect routes that require authentication. It checks if the JWT token and `Content-Type` headers are present in the request. If they are missing, it returns a JSON response indicating the missing headers with a status code of 401 (Unauthorized). If the headers are present, it attempts to decode the JWT token using the provided secret key. If the decoding fails, it returns a JSON response indicating an invalid token with a status code of 403 (Forbidden). If the decoding is successful, the decorated function is called.
6. The `__name__ == "__main__"` block is used to prevent the script from running when imported as a module.

Overall, this code provides a basic JWT authentication mechanism for protecting routes in a Flask application. It generates and decodes JWT tokens, and the `token_required` decorator can be applied to specific routes to enforce authentication.


#### Mail server

The provided code is a Python script that handles sending emails using the SMTP protocol. Here's an overview of what the code does:

1. It imports necessary modules including `smtplib`, `ssl`, `MIMEMultipart`, `MIMEText`, `Path`, `json`, and `os`.
2. The `Message` class represents an email message. It initializes a `MIMEMultipart` object and sets the subject, sender, receiver, and body of the email. The `get_message` method returns the constructed message.
3. The `MailServer` class represents the mail server configuration. It reads the configuration from a JSON file (`configs.json`) located in the parent directory of the script. It sets the server hostname, port, login email, and login password.
4. The `send` method of the `MailServer` class takes a `message` object and sends it via a secure connection to the configured mail server. It uses the `smtplib` module to establish a connection, logs in using the provided email and password, and sends the email using the `as_string` method of the `MIMEMultipart` message.
5. The `load_reset_template` function reads the content of a "reset_password_template.html" file located in the same directory as the script and returns its contents as a string. It is used to load the HTML content for a reset password email template.
6. The `load_confirmation_template` function reads the content of a "confirmation_template.html" file located in the same directory as the script and returns its contents as a string. It is used to load the HTML content for an account confirmation email template.
7. The `__name__ == "__main__"` block is used to prevent the script from running when imported as a module. It creates an instance of the `MailServer` class.

Overall, this code provides a basic email-sending functionality using the SMTP protocol. It allows you to construct email messages, configure the mail server settings, and send the messages using the configured mail server. Additionally, there are helper functions to load email template contents from HTML files.

#### Database

The provided code is a Python script that defines a `DatabaseAPI` class for interacting with a MongoDB database using the `pymongo` library. Here's an overview of what the code does:

1. It imports necessary modules including `pymongo`, `ObjectId` from `bson.objectid`, `Optional`, `List`, and `json`.
2. The `DatabaseAPI` class represents the database API. It initializes the MongoDB URI and database name, establishes a connection to the MongoDB database, and sets the database connection.
3. The `createRecord` method inserts a new record into the specified collection. It takes a `data` parameter (dictionary containing the record data) and a `collection` parameter (the name of the collection to insert into). It inserts the `data` into the specified collection and returns the inserted document's ID.
4. The `getRecordById` method retrieves a record from the specified collection by its ID. It takes a `recid` parameter (dictionary containing the ID of the record to retrieve) and a `collection` parameter (the name of the collection to search in). It retrieves the record from the collection based on the `_id` field and returns the record as a dictionary or `None` if not found.
5. The `updateRecord` method updates a record in the specified collection. It takes a `recid` parameter (the ID of the record to update), a `data` parameter (dictionary containing the updated data), and a `collection` parameter (the name of the collection to update in). It checks if the record with the given ID exists, and if it does, it updates the record with the new data and returns the MongoDB `update_one` result. If the record does not exist, it returns -1.
6. The `deleteRecordById` method deletes a record from the specified collection by its ID. It takes a `recid` parameter (the ID of the record to delete) and a `collection` parameter (the name of the collection to delete from). It retrieves the record using the `getRecordById` method, deletes the record from the collection, and returns the deleted record as a dictionary.
7. The `getRecords` method retrieves records from the specified collection based on the given query criteria. It takes a `data` parameter (dictionary containing the query criteria) and a `collection` parameter (the name of the collection to search in). It retrieves the records from the collection based on the query criteria and returns a list of dictionaries representing the retrieved records.

Overall, this code provides a basic API for performing CRUD (Create, Read, Update, Delete) operations on a MongoDB database using the `pymongo` library. It allows you to create, retrieve, update, and delete records in a MongoDB collection, as well as retrieve multiple records based on query criteria.

#### Configs

The provided JSON represents a configuration file with various settings. Here's a breakdown of the key-value pairs in the JSON:

- `"secret_key"`: A secret key used for encoding and decoding JSON Web Tokens (JWTs).
- `"time_window_in_minuts"`: The time window (in minutes) used for JWT expiration.
- `"DB_URI"`: The URI or connection string for connecting to the MongoDB database. In this case, it's set to `"mongodb://localhost:27017"`, indicating a local MongoDB server running on the default port.
- `"DB_NAME"`: The name of the MongoDB database to connect to.
- `"frontend_link"`: The link or URL for the front-end application associated with this configuration.
- `"mail_server_email"`: The email address associated with the mail server used for sending emails.
- `"mail_server_password"`: The password for the mail server email account.
- `"mail_server_host"`: The hostname or address of the mail server.
- `"mail_server_port"`: The port number used for the mail server connection. In this case, it's set to `465`, which typically corresponds to SMTP over SSL/TLS.

These settings can be used by an application to configure various aspects such as authentication, database connection, front-end integration, and email server settings.

### Resources
- [JWT Debugger](https://jwt.io/)
- [python-jwt](https://github.com/GehirnInc/python-jwt)
- [How to Rate Limit Routes in Flask](https://medium.com/analytics-vidhya/how-to-rate-limit-routes-in-flask-61c6c791961b)


### Acknowledgement

I would like to extend my heartfelt appreciation and recognition to the following individuals for their exceptional contributions and unwavering dedication throughout the development of our backend project:


**@habibaelsayed**: I express my deepest gratitude for your attention to details. Your valuable suggestions have played a significant role in enhancing the overall quality of our project. The simplest contributions can be essential and vital steps to achieving great things, so never underestimate anything.

**@Marconoyet**: Thank you, my brother, for everything. All the problems that you found in the project and that you alerted me to. All of that helped in completing the project in the best way possible. Thank you. I hope you will forgive me at any time when I got angry and was unbearable, but that is what brothers do, right?

**@tlynx538**: I'm happy and grateful to you for your help in solving one of the problems that we encountered during the implementation of the project. We wish you success.

We would also like to acknowledge the support and contributions of our wider community of developers, open-source contributors, and online resources. Their collective knowledge and expertise have been an essential source of inspiration and guidance throughout our project journey.

-Hossam Hamdy 

---

<div align="center">
مسك الختام 💙
</div>
