## Testing throughput on a 200Gb/s Ethernet device.

For the test case portion you do not need to write the actual test.

Just provide a good description of the test scenario(s), setup and teardown, tools used in testing and pass/fail criteria for each scenario.

---

Whenever I consider testing a network adapter, I usually reach for `iperf3`.  This is very easy to setup and do a basic test in the client/server model, testing both downloading and uploading (although, it'd be good to at least skip the first results because of `TCP` slow start).

Best way to test would be on a local network where one has complete control over the topology and the devices.

The test scenarios could be:

1. Only one machine (the test machine) is transmitting.
    - Client and server are on the same network.
    - Client and server are on different networks.

1. Multiple machines are transmitting.
    - Clients and server are on the same network.
    - Clients and server are on different networks.

For each test scenario:

- Test different transaction rates:
    + per second
    + per minute
    + per hour
    + per day
- Test both `TCP` and `UDP`.
- Is the adapter a wired device? Wireless?  Can both be tested?  Of course, the latter is more susceptible to jitter because of noise.
- Adjust `TCP` window size to be larger if there are preliminary tests that determine the network is reliable (and Linux kernels from 2.6.8 support `TCP` Window Scaling by default, `net.ipv4.tcp_window_scaling`).
- Increasing the `MTU` size may help as well, especially if not testing applications who transmits in short messages.  Use the largest size `MTU` that the adapter and the network can support.
- Enable full-duplex mode.
- Enable `CPU` pinning (if doing so, will need additional tools to prevent other system processes from using the pinned `CPU`s).
    + This wouldn't help troubleshooting a network issue, but may help to improve throughput.

## Setup and teardown:

- Use Terraform and Ansible to setup and teardown the machines.
- Use [iperf3 python wrapper](https://iperf3-python.readthedocs.io/en/latest/) or something similar to automate.

## Pass/Fail Criteria

To be honest, I'm not entirely sure what would be considered a fail scenario.  For instance, what percentage of packet loss and subsequent retransmission would constitute a failure for varying bitrates measured per second, per minute, etc?

Since maximum bandwidth is unattainable, what percentage below that would be considered acceptable enough to pass?  70%?  80%?

Over the years, I've measured thoughput and in different scenarios as I've laid out here, but I've never set benchmarks as to what constitutes a pass and what constitutes a failure.  I've done a lot of searching on the Internet to try and get some idea, but I've been surprised by the lack of information I've found.

I'm very keen on learning more about this, and I certainly would like to have the time to be able to really dig in and learn about effective test strategies.

## Notes:

- Of course, the network would need to have links that support bandwidth at least that of the Ethernet device.
- This assumes that it's able to test a connection between devices that are able to run `iperf3`.  So, we're assuming that it's not testing a connection between a host machine and a router, for instance.

