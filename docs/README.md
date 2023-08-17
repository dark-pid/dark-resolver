# dARK Resolver

## dARK Resolver Isseus

- How to deal when an external pid is assigned to multiples PIDs?


The dARK Resolver is a simplified version of the ARK resolver designed to handle Persistent Identifiers (PIDs). PIDs are used to uniquely identify digital objects and provide a consistent way to access them regardless of changes in location or metadata.

## Goals

The primary goals of the dARK Resolver project are:

1. **Simplified PID Resolution**: Provide a straightforward method to resolve PIDs to their corresponding URLs, focusing on efficiency and ease of use.

2. **Blockchain Integration**: Utilize blockchain technology to store and retrieve PID data, ensuring secure and tamper-proof identification and resolution.

3. **Protocol Agnostic**: Develop a resolver that supports various PID systems, such as DOI, ARK, CCN, and more. While initial implementation covers DOI and ARK, the design allows for future expansion to additional protocols.

## Functionality

The dARK Resolver currently offers the following functionality:

### 1. PID Protocol Identification

When a user queries the dARK Resolver, the resolver performs a protocol identification process:

- If the queried PID belongs to the dARK protocol, the resolver proceeds to resolve it using the dARK-specific logic.
- If the PID belongs to another supported protocol, such as ARK or DOI, the resolver redirects the query to the respective protocol's resolver.
- If the PID belongs to an unsupported protocol or is invalid, an error is reported.

### 2. dARK Resolution

#### ARK PIDs

For ARK PIDs, the resolver performs the following steps:

1. Check if the PID belongs to the dARK protocol.
2. If yes, retrieve the URL from the PID metadata.
3. If not, create a query to the ARK global resolver and obtain the URL.
4. Redirect the user to the resolved URL.

#### DOI PIDs

For DOI PIDs, the resolution process involves:

1. Determine if the DOI corresponds to a dARK PID.
2. If so, use the DOI to retrieve the associated dARK PID.
3. If not, query the DOI resolver to get the URL.
4. Redirect the user to the resolved URL.

### 3. Redirecting Users

Once the PID is resolved to a URL, regardless of the protocol, the dARK Resolver redirects the user to the appropriate URL, allowing seamless access to the desired digital object.

## Contribution

We welcome contributions from the community to enhance the functionality, add support for new protocols, improve blockchain integration, and more. Feel free to fork this repository, make your changes, and submit pull requests. Together, we can make PID resolution more efficient and versatile.

For more details, refer to our [Contribution Guidelines](link-to-contribution-guidelines).

## Get Started

To start using the dARK Resolver, follow the steps outlined in our [Installation Guide](link-to-installation-guide). This guide will walk you through setting up the resolver, querying PIDs, and leveraging its capabilities.

## Contact

If you have questions, suggestions, or feedback, please reach out to our team at [contact@email.com](mailto:contact@email.com).

---

Remember to replace placeholders like "link-to-contribution-guidelines" and "link-to-installation-guide" with the actual URLs of your contribution guidelines and installation guide.
