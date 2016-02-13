# Qumulo App version 1.2.22

## Overview

Qumulo Cluster integration app for Splunk

## Dependencies

Qumulo REST API
croniter
six

## Open Source Software


Licended under Educational Community License (ECL) Version 2.0, April 2007

http://www.osedu.org/licenses/

The Educational Community License version 2.0 ("ECL") consists of the Apache 2.0 license, modified to change the scope of the patent grant in section 3 to be specific to the needs of the education communities using this license. The original Apache 2.0 license can be found at: http://www.apache.org/licenses/LICENSE-2.0

See project file LICENSE for details and terms


## Supported Splunk Versions

Verified with Splunk 6.3

## Setup

Copy files to $SPLUNK_HOME/etc/apps/qumulo_splunk_app and restart Splunk

## Configuration

You'll need to provide hostname, port number and username and password for an account
with access to Qumulo REST API after installing the app.

You can also configure different poll intervals for each endpoint etc.

## Splunk Meta Data

The Qumulo Splunk app creates a new index (qumulo)

## CIM

Qumulo Splunk App defines three source types:

[qumulo://get_iops]
[qumulo://get_capacity]
[qumulo://get_throughput]

## Distributed deployment

This app is designed to run in context of a Splunk server and communicates via REST 
with a Qumulo cluster.

## Additional declarations

## Using

* any other information that is pertinent to using the App.

## Logging

Any log entries/errors will get written to $SPLUNK_HOME/var/log/splunk/splunkd.log

## Troubleshooting

* Any troubleshooting steps that may be useful for the user to work through to resolve issues

## Contact and Support

http://qumulo.com

Support hours (at least 8 hours a day, 5 days a week)
How to get support (email, website, phone):
mmurray@qumuloc.com

Issues with this application are tracked using GitHub issues on the associated project, which
you can find here:

https://github.com/Qumulo/qumulo_splunk_app
