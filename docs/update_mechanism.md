## Update Mechanism

When a new institution is added to the system, the dARK API immediately sends a notification to the Resolver. Upon receiving the notification, the Resolver updates its configuration to allow queries involving the new NAAN (Name Assigning Authority Number). Once the NAAN is added to the dARK Resolver, all registered PIDs (persistent identifiers) associated with that NAAN become available for real-time query.

The diagram outlines the update mechanism within a system designed to maintain current information about institutions, represented by unique identifiers known as NAANs (Name Assigning Authority).

```mermaid
sequenceDiagram
    autonumber

    participant CS as dARK <br> API
    participant BC as Blockchain
    participant RS as dARK <br> Resolver

    alt MECHANISM 1
        CS ->> RS: notify new NAAN
        RS ->> RS: enable query for new NAAN
    end


    %% implementar no futuro
    loop MECHANISM 2
        RS ->>+ BC: query for new NAAN
        BC -->>- RS: send the available NAANs
        RS ->> RS: enable query for new NAAN
    end
```

> **Mechanism 1:** When a new institution is added to the system, the [dARK API](./05_dark_api.md) notifies the `Resolver`. Upon receiving this notification, the Resolver adjusts its settings to allow queries regarding the newly added NAAN.
>
> **Mechanism 2:** This mechanism illustrates a continuous update loop. The Resolver periodically queries the `Blockchain` for any updates regarding NAANs. Upon receiving a response from the `Blockchain`, which contains information about available NAANs, the Resolver updates its query capabilities to include these new entries.
> 

In essence, these mechanisms ensure that the Resolver component of the system remains updated with the latest information about institutions, facilitating efficient resolution of persistent identifiers associated with these entities


It is important to mention that once that the NAAN is added to the `dARK Reslover` the PID created are available to queried by the resolver. In other words, the update mechanism is only to add new NAAN to the resolver the PID are available in realtime.
