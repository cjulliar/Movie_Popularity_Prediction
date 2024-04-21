
# Prediction of Movie Popularity for "New is always better" Cinema

## Project Description

This project aims to develop a decision-making tool for the "New is always better" cinema, enabling the prediction of movie popularity during their first week of screening. The goal is to optimize the weekly programming of movies based on their potential to attract audiences, utilizing machine learning techniques to estimate attendance. The tool will be accessible via a web application, simplifying its use for the cinema manager without the need for in-depth technical skills.

## Context

The "New is always better" cinema exclusively screens new releases during their first week, with a weekly rotation of movies. Facing the challenge of efficiently selecting films to screen, this tool aims to partially automate the decision-making process by relying on data and predictions rather than intuition and experience.

## Main Features

- **Estimation of Movie Popularity:** Use of a regression algorithm to predict a movie's number of entries before its release, based on characteristics such as genre, nationality, fame of actors and directors, and potentially the buzz on social networks.
- **Automatic Selection of Movies:** Weekly choice of two movies to screen, based on attendance estimates.
- **Interactive Dashboard:** Display of predictions, selected movies, revenue estimates, and comparison with actual results for continuous adjustment and improvement.

## Technologies Used

- **Python:** Main language for developing the machine learning model and data scraping.
- **Django & Tailwind CSS:** For web application development.
- **Scrapy:** Scraping tool to collect data necessary for model training.
- **FastAPI:** To expose the machine learning model via an API.
- **MLflow & Azure Machine Learning Studio:** For managing machine learning experiments.
- **Docker:** Used to containerize the application's different components for simplified deployment.
- **Jira:** Project management tool to implement agile methodology.

## Architecture

The project follows a microservices architecture, with:

- A machine learning API developed with FastAPI to expose the model.
- A Django web application consuming this API to display predictions and analytical data.
- Two databases: a transactional one for the application and an analytical one for the data needed by the model.
- Automation of scraping for weekly data updates.

## Agile Development

- The project is developed following agile methodology, divided into 4 one-week sprints.
- The roles of Scrum Master and Product Owner are assigned and rotate among team members for each sprint.

## Deliverables

- Functional specifications document
- Analytical and transactional databases
- Machine learning model
- API exposing the model
- Web application
- Source code on Github
- Presentation support

## Project Evaluation

The project's success will be measured through the accuracy of the machine learning model's predictions, the functionality and usability of the web application, and the client's satisfaction in terms of ease of use and impact on cinema management.

## Getting Started

To launch the application on your local system, please follow the setup and installation instructions available in the docs/installation folder of the project's GitHub repository.

### Webapp

In order to launch the webapp on your local system, you first need to create a .env file in the webapp folder.
Here is the environment variables that the .env should include :
```
SECRET_KEY='your-secret-key'
DEBUG=1
ENVIRONMENT='dev'

HOST_MYSQL= "your-mysql-host"
USER_MYSQL= "your-user"
PASSWORD_MYSQL= "your-password"
DATABASE_MYSQL= "your-database"
```

## Contribution

We welcome contributions from the community! To contribute, please follow the instructions available in the CONTRIBUTING.md file.

## License

This project is distributed under the MIT license. For more details, see the LICENSE.md file.
