# flask-reqcheck

Validate requests to a flask server using Pydantic models.

## Motivation

The purpose of Flask-Reqcheck is to check (i.e. validate) requests against a [Pydantic](https://docs.pydantic.dev/latest/) model, and to implement this in the most straightforward way possible (every Flask user's friend - a decorator).

I had already began implementing this before I saw that [Flask-Pydantic](https://github.com/bauerji/flask-pydantic) exists. However, Flask-Pydantic no longer works since Pydantic 2.x. I could have attempted to make some PRs to build on that, but I decided against that because I wanted to continue building this for myself (and there was just more code in Flask-Pydantic than I felt was necessary to accomplish my main goal). Ultimately, I wanted to have something small that I can import when using Flask, but I decided to host it here in case others want to use it too. Either way, this project is partly inspired by Flask-Pydantic.

## Installation

pending

## Usage

pending

## Contributing

pending

## To-Do

- Handle query parameters:
  - list
  - multiple definition (see Pet Store's [findPetsByTags](https://petstore3.swagger.io/#/pet/findPetsByTags))

## License

MIT
