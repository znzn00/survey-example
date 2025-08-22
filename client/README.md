# Angular
It's divided into two projects that may reuse certain components. But logically should work the same.

It should consists of:
* Shared: The library that contains most of the backbone.
* Server-Side Rendering (SSR).
* Client-Side Rendering (CSR): Planned.

## Why is SSR and CSS divided? 
Because it follows two distinct design philosophies, SSR wants to build the view on the server before sending it to a client (in this case, a web browser), meanwhile CSR wants to send all required parts for a view for the client and instruction on where each part is to be inserted.

SSR is way more lightweight for clients to compute, but heavier on the server to prepare, and in reverse in CSR.