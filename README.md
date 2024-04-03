# Introduction
This is a teaching material aimed to demonstrate the peculiarities of testing distributed systems. More specifically, this repo illustrates the foundational principles of service virtualization using [mountebank](https://www.mbtest.org/)[^1]. The following topics are covered in this unit:

- Why there is a need for service virtualization in testing distributed systems.
- Demonstration of the basic principles of service virtualization using mountebank, and it's Python binding called [mbtest](https://pypi.org/project/mbtest/).
- The differences between stubs and mocks as well as the importance of knowing when to use each of them. It is far more important to understand the implications of using one or the other than to uncritically accept and stick to a particular style (a debate known as _mockists vs. classicists_). Hence, the [Mocks Aren't Stubs](https://martinfowler.com/articles/mocksArentStubs.html) blog's value is in its ability to explain the trade-offs between the two styles rather than about finding the "right" answer should you be a mockist or a classicist.
- How to virtualize a mail server to test your client.
- How to virtualize a RESTful service to test your REST client.
- How various authentication & authorization methods work and how can be tested in a controlled environment.
- Why virtual development/runtime environments are so important, and how to make one leveraging the standard Python 3+ and JavaScript toolset.

# Architecture of Distributed Tests with Virtualized Services
The main objective of service virtualization is to run tests in a manner that is opaque for a system under test (sut). In other words, a sut thinks that it is communicating with a real backend server. It is possible to check both the responses (verification of state changes) and the requests (verification of behavior). The latter is especially useful when you want to check if a sut is sending the correct commands to the backend server's API and/or stick to the protocol. The next figure[^2] illustrates the architecture of distributed tests with service virtualization and explains how mountebank responds to requests. 

<kbd>![How Testing Services with mountebank Works](https://freecontent.manning.com/wp-content/uploads/mentalmodel-testing-microservices-with-mountebank2.png)</kbd>

*Figure 1 - How testing with mountebank works. One important technical detail is the usage of the [canonical data model](https://www.enterpriseintegrationpatterns.com/patterns/messaging/CanonicalDataModel.html), which isolates you from the specifics of protocols while defining rules for imposters.*

# Usage
It is assumed that all commands below will be executed from the project's *root* folder as well as that this repo 
was cloned from GitHub and is available on your machine. Furthermore, you must have Python 3.10+ 
installed and exposed as `python` as well as it's package manager as `pip`. 
If this is not the case, then you will need to adjust the instructions below accordingly. Windows users are
expected to use the [Cygwin](https://www.cygwin.com) environment.

The table below explains the directory structure of this repository.

| Folder    | Description                                                                      |
|-----------|----------------------------------------------------------------------------------|
| *root*    | Contains the package dependencies for Python and NodeJS.                         |
| `suts`    | Systems under test that will be exercised via virtualized services.              |
| `tests`   | Contains the [Pytest](https://docs.pytest.org/) tests.                           |

## Setup of the Python Related Environment
For educational purposes all steps related to handling a virtual environment are explicitly enrolled and expected to be manually executed. You can automate
all these steps. for example, using Codespaces.
1. Execute the next step only once inside the cloned project:
   ```bash
   python -m venv .venv
   ```
2. At the beginning of a session active your virtual environment by running:
   ```bash
   source .venv/bin/activate
   ```
   As a sanity check you may want to run `echo $VIRTUAL_ENV` to see if the environment is activated.
3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
4. List the available packages to verify that everything is installed correctly:
   ```bash
   pip list
   ```
   This should produce an output that includes the following item:
   ```
   Package Version
   ------- -------
   mbtest  2.12.0
   <other dependencies>
   ```
5. Deactivate the virtual environment once you are done running this project:
   ```bash
   deactivate
   ```
The advantage of using a virtual environment is that it allows you to work on multiple projects with different 
dependencies without them interfering with each other. It also makes it easy to share your project with others, 
as they can create the same environment on their machine.

## Setup of mountebank
The following steps are required to set up mountebank:

1. Install [Node Version Manager (nvm)](https://github.com/nvm-sh/nvm) and use Node version 20.10 or higher.
2. Run `npm install mountebank` to install mountebank locally. It is also possible to install it globally as well as [use with Docker](https://mbtest.readthedocs.io/en/latest/guide/docker.html). Nevertheless, the latter requires explicitly opening up a port for each imposter, which is done automatically if mountebank is started via `npx` or `npm`.
3. Run `npx mb --version` to verify that mountebank is installed correctly. You should see `2.9.1` or higher.

## Running Distributed Tests
The tests are located in the `tests` directory. They will be separately described in the following sections. This section covers common steps to run the tests. Before executing any test, ensure that mountebank is running in the background. This can be achieved by running the following command[^3]:
```bash
npx mb
```
I suggest that you run this command in a separate terminal window. This way, you can keep it running while you run tests in another window. If you encounter any error, like, any of the ports being already in use, then you can change the port number in the test configuration file or stop the process that is using the port. The configuration parameters for all tests are inside the `tests/.env.test` file. It is fully commented, so you should have no difficulty in understanding it. The same is true for all sorts of source files, both for tests and components.

### Running the Mail Client Test
Execute: 
```bash
PYTHONPATH=. pytest tests/test_mail_client.py
``` 
This will test the `suts/mail_client.py` module by sending a dummy email message to contrived recipients. Mountebank will record the requests and the test will verify that the client is sending the correct commands to the mail server. This is a perfect example of mocking, [learn more](https://www.mbtest.org/docs/api/mocks).

### Running the Album Viewer Test
Execute: 
```bash
PYTHONPATH=. pytest tests/test_album_viewer.py
```
The album viewer test is more complex than the mail client test:
1. It runs the _album viewer_ module that uses the [Spotify Web API](https://developer.spotify.com/documentation/web-api) (from now on denoted just as Spotify API) to retrieve an access token and some albums. Mountebank will emulate the real Spotify service and send back correct responses expected by the system under test.
2. The test verifies that the client is getting correct responses. This is a perfect example of using [stubs](https://www.mbtest.org/docs/api/stubs).

## Configuring the Applications for Production Use
The mail client's source code contains instructions how to obtain an application password from Google to use the Gmail API.

The album viewer must be able to retrieve an access token to use any Spotify API endpoint. This entails registering a Spotify application and obtaining the client ID and client secret. The following steps are required to do this:
1. Create a Spotify developer account [here](https://developer.spotify.com/), as needed. 
2. Create an application via Spotify [dashboard](https://developer.spotify.com/dashboard) to obtain the client ID and client secret. To keep things simple put `http://localhost/` as the redirect URI and select Web API.
3. Call `suts/album_viewer.py#get_access_token` function from your program passing the above-mentioned credentials. 

# Conclusion
This project has demonstrated a miniscule subset of possibilities that service virtualization offers. It is a powerful tool that can be used to test distributed systems in a controlled environment. We have focused mostly on testing functionality, but mountebank can be efficiently used to test performance as well. The latter is especially important when you want to test how your system behaves under extreme load without inadvertently summon a DDoS attack on a remote dependency. Simulation of faults is also nearly impossible without some form of service virtualization, [learn more](https://www.mbtest.org/docs/api/faults).

As a side note, an imposter can proxy any up so far unmatched requests toward the target system (known as a [self initializing fake](https://martinfowler.com/bliki/SelfInitializingFake.html)), and tests will implicitly verify correctness of the client's requests as well (since they are also hitting real backend endpoints). In other words, they will inherently perform a [contract test](https://martinfowler.com/bliki/ContractTest.html) ensuring that nothing has changed in the Spotify API.

[^1]: There are many other good alternatives, like, [WireMock](https://wiremock.org/). Nonetheless, all of them follow and deliver the same basic principles and features.
[^2]: This freely available image was taken from the accompanying [site](https://www.manning.com/books/testing-microservices-with-mountebank) associated with the book about mountebank.
[^3]: There are lots of command line options, just run `npx mb --help` to read about them.
