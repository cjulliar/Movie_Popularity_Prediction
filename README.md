#README - Movie Popularity Prediction for "New is always better" Cinema
#Project Description

This project aims to develop a decision-making tool for the "New is always better" cinema, designed to predict the popularity of films during their first week of showing. The goal is to optimize the weekly film programming based on their potential to attract audiences, utilizing machine learning techniques to estimate attendance. The tool will be accessible through a web application, simplifying its use for the cinema manager without the need for extensive technical skills.
Context

"New is always better" cinema exclusively showcases new releases during their first week, with a weekly rotation of films. Faced with the challenge of efficiently selecting films to screen, this tool seeks to partially automate the decision-making process by relying on data and predictions rather than intuition and experience.
Main Features

    Popularity Estimation of Movies: Uses a regression algorithm to predict a film's attendance before its release, based on features such as genre, nationality, the fame of actors and directors, and potentially the buzz on social media.
    Automatic Film Selection: Weekly choice of two films to screen, based on attendance estimates.
    Interactive Dashboard: Displays predictions, selected films, revenue estimates, and comparisons with actual results for continuous adjustment and improvement.

#Technologies Used

    Python: The main language for developing the machine learning model and data scraping.
    Django & Tailwind CSS: For web application development.
    Scrapy: Data scraping tool to collect data needed to train the model.
    FastAPI: To expose the machine learning model via an API.
    MLflow & Azure Machine Learning Studio: For managing machine learning experiments.
    Docker: Used to containerize the application's different components for simplified deployment.
    Jira: Project management tool to implement agile methodology.

#Architecture

The project follows a microservices architecture, with:

    A machine learning API developed with FastAPI to expose the model.
    A Django web application consuming this API to display predictions and analytical data.
    Two databases: one transactional for the application and one analytical for the data needed by the model.
    Automation of data scraping for weekly data updates.

#Agile Development

    The project is developed following agile methodology, divided into 4 one-week sprints.
    The roles of Scrum Master and Product Owner are assigned and rotated among team members for each sprint.

#Deliverables

    Functional specifications document
    Analytical and transactional database
    Machine learning model
    API exposing the model
    Web application
    Source code on Github
    Presentation support

#Project Evaluation

The success of the project will be measured through the precision of the machine learning model's predictions, the functionality and usability of the web application, and the client's satisfaction in terms of ease of use and impact on cinema management.
Getting Started

To launch the application on your local system, please follow the setup and installation instructions available in the docs/installation folder of the project's Github repository.
