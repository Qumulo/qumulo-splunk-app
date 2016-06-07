# Qumulo App version 2.0.0

## Overview

The Qumulo Splunk App (https://github.com/Qumulo/splunk_app) lets Qumulo (http://qumulo.com) customers 
use Splunk to view metrics and create alerts about their Qumulo cluster.


## Dependencies

Qumulo REST API/ python 2.7 wrapper (https://pypi.python.org/pypi?%3Aaction=pkg_edit&name=qumulo_api)
croniter
six

## Supported Qumulo Core / Cluster versions

The Qumulo Splunk App is verified to work with:

Qumulo 2.0.0
Qumulo 1.3.0
Qumulo 1.2.23
Qumulo 1.2.22
Qumulo 1.2.21

Earlier or later version of Qumulo Core may also work with this version of Qumulo Splunk App but have not been
verified with this version.

## Open Source Software

Licensed under Educational Community License (ECL) Version 2.0, April 2007

http://www.osedu.org/licenses/

The Educational Community License version 2.0 ("ECL") consists of the Apache 2.0 license, modified to change 
the scope of the patent grant in section 3 to be specific to the needs of the education communities using this license. 
The original Apache 2.0 license can be found at: http://www.apache.org/licenses/LICENSE-2.0

See project file LICENSE for details and terms


## Supported Splunk Versions

Verified with Splunk 6.3

## Setup

Copy files to $SPLUNK_HOME/etc/apps/qumulo_splunk_app and restart Splunk

## Installation and Configuration

You'll need to provide hostname, port number and username and password for an account
with access to Qumulo REST API after installing the app.

You can also configure different poll intervals for each endpoint etc.

**NOTE** that you will need to restart your Splunk server after updating configuration.

## Splunk Meta Data

The Qumulo Splunk app creates a new index (qumulo) with three sourcetypes (described below)

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

Clicking on 'Qumulo App' on the left-hand side in the Splunk home screen brings you to the default / provided 
Qumulo dashboard.  It can be customized as-needed.  By default it shows:

Minimum and Average Free Capacity  charts
Read and Write Throughput values over time
Most Active Client IPs against the cluster, over time

These are suggested metrics to display in the dashboard.  By clicking on the Qumulo Splunk App icon, you can search
any of the Qumulo metrics and create appropriate dashboard components or alerts or replace the existing dashboard 
components.

Clicking on 'Search' in the Qumulo Splunk App navigation bar will let you search on any one of IOPs, capacity or
throughput.  

Clicking on 'Setup' in the Qumulo Splunk App navigation bar will let you set up or edit parameters for the app,
enable or disable endpoints, control polling frequency for each of the three REST inputs or view any errors
that have occurred within the Qumulo Splunk App.


## Logging

Any log entries/errors will get written to $SPLUNK_HOME/var/log/splunk/splunkd.log

## Troubleshooting

Clicking on 'Manage/ Qumulo Splunk App Errors' in the Qumulo Splunk App navigation bar will show any errors that
have occurred while running the Qumulo Splunk App; Errors can be queried and filtered just like any other data in
Spllunk.

## Contact and Support

http://qumulo.com

Support hours (at least 8 hours a day, 5 days a week)
How to get support (email, website, phone):
Michael Murray
mmurray@qumulo.com
http://qumulo.com
855 4-QUMULO (855.478.6856)


Issues with this application are tracked using GitHub issues on the associated project, which
you can find here:

https://github.com/Qumulo/splunk_app
