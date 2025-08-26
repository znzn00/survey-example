# survey-example
Projects to showcase my skills and knowledge across multiple technologies.

All projects will be used to make a survey system, which consists of creating surveys and collecting it's completed questionnaires.

All projects will never be ready for production as most of them are showcases of how I work and won't have all the best practices for some implemetations, security or features:
* Password hashing: It will be just a simple MD5 hash, because it's lightweight and it's just there to showcase the process.
* Refresh token for JWT: Another JWT instead of the best practice which is the implementation of rotating tokens.
* CSRF or XSS protection: Those aren't necesary as the project won't be production ready.
* CORS configuration: Allowing everything just to save time configuring it correctly.

## Currently working on:
A simple HTTP server on Python and Angular 19 Server-side Rendered APP.

## What will the project consist of?
* Server: Contains all servers, backend or fullstack.
* Clients: Contains all client.

### Servers
All servers should be able to serve the application without any clients, or with clients via the usage of APIs.

* Fullstack
* * Plain HTML, CSS and JS.
* * HTMX
* API
* * RESTful
* * GraphQL

### Clients
All clients will consumes APIs from servers, with configurations to run depending on what type of API.

### Sessions 
Only required to create new users, questions, surveys, etc...

Won't be required in order to answers surveys.
#### Fullstack
All sessions will be HTTP-only Cookie.
#### Front-end with Back-end
It will be managed with JWT, having access and refresh tokens.