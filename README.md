# Reddit r/place worker

This is a python project by Comet team that helps users to create multiple reddit accounts without captcha blocking. It requires Python 3.8 or higher to run. Below are the instructions to set up the project environment, configure necessary settings, and run the code.

## Installation

To manage project dependencies and create a virtual environment, we use pipenv. If you don't have pipenv installed, you can install it using pip:

```
pip install pipenv
```

After installing pipenv, navigate to the project directory and run the following command to install the project dependencies:

```
pipenv install
```

## Setting up .env file

The project uses a .env file to store configuration variables. Before running the code, you need to create a .env file in the root directory of the project. The .env file should have the following content:

```
DBC_USERNAME=value1
DBC_PASSWORD=value2
```

## Running the code

To run the Python code in the virtual environment created by pipenv, use the following command:

```
pipenv run python src/main.py
```

That's it! You should now have the project set up and be able to run the code successfully. If you encounter any issues or have questions, feel free to contact the project maintainers or open an issue on the project repository.

Happy coding!
