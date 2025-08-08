## 🏗️ FastAPI + MongoDB Task Manager API

 created a system That user can shedule their task in calendar dashboard  It was created as a learning experience to explore modern backend development with FastAPI, asynchronous API design, and integration with NoSQL databases.

<br>

## 🔧 Key Features
- ✨ Full CRUD operations for tasks

- 📆 Integration with FullCalendar for interactive scheduling

- 🔐 User authentication and task ownership suppor.

- ⏱️ Task due dates with proper ISO handling

- 🧾 Formik for task form handling in the frontend

- 🌐 Frontend built using React, Tailwind CSS, and ShadCN UI

  <br>

## 🛠️ Installation Guide
Follow these steps to set up the project on your local machine:

```
git clone https://github.com/Mhd-Asjad/PlanIt.git
cd server

```
***2. Create a Virtual Environment***
```

python -m venv env
source env/bin/activate  # On Windows use: env\Scripts\activate

```

***3. Install Dependencies***

```

pip install -r requirements.txt

```

***4. Set Up Environment Variables***

Create a .env file at the root with the following content:

```

MONGODB_URI=mongodb://localhost:27017
SECRET_KEY=your_secret_key

```
Update the values as per your setup.

***5. Run the Server***

```

uvicorn main:app --reload

```

The API will be available at:
-📍 http://127.0.0.1:8000


### 📬 API Endpoints


**auth**

POST api/user/register - for registering new user

POST api/user/login - user login

GET api/user/me - get user info 

**Task**

POST api/task/create – Create a new task

PATCH api/task/update/{id} – Update existing task

GET api/task/list – Get all tasks for a user

DELETE api/task/delete/{id} – Delete a task






