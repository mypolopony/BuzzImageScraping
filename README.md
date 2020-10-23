# Google Image Scraping with Celery and Selenium

### Problem Statement
The predictive power of an image-based machine-learning system, like all ML endeavours, relies heavily on both the quantity and quality of training data. As Google Images is an obvious source of imagery, it has long been a target for scrapers.

In the early days, the Google Images results were presented with pagination; that is, a certain number of resulst would be shown above a "Next" and "Previous" button. In addition, since the page number was embedded in the results URL, one could skip to any arbitrary page. That format made it very easy to scrape programatically. Sadly, that results format has not been seen in nearly a decade.

Several years ago, Google opened up APIs for core services, including Images. This allowed for rate-limited access and was even free for an individual, allowing a decent number of requests. Also sadly, Google closed its public APIs some years ago.

Now, there are third party (subscription) scraping services with more advanced technology to evade detection. 

However for small-to-medium sized operations like ours, it is still possible to grab imagery at a leisurely rate without alerting Google.

### Outline
Scraping is a network-bound operation (rather than being CPU-bound). This means that a single process will spend a lot of time waiting to download. 

Multithreading is an option but here we use Celery, an asynchronous message queue that will allow us to use the primary program to search for links and then send them to any number of (potentially distributed) workers, ready to download the actual imagery.

The URI-finding primary program will use a pseudobrowser (also called web driver) that acts just like a real browser and can emulate all of the actions a real user might use. In the old days, we could navigate programatically using `requests` and `urllib` but because Google Image results utilize an infinite scroll, it's necessary to "interact" with the site using the more heavy-handed web driver. 

### Project Description
Celery is a Python Task-Queue system that handle distribution of tasks on workers across threads or network nodes. The application pushes messages (in this case, image URIs) to a broker (in this case, RabbitMQ) and Celery workers will pop them and schedule task execution.

The relevant pieces of the project are as follows:

- `celery.py` simply initializes the application and connects to the (RabbitMQ) broker. It also brings the worker tasks into scope.
- `chromedriver` is the aformentioned pseudobrowser (Chrome version and archicecture specific, available [https://sites.google.com/a/chromium.org/chromedriver/downloads], mine is precompiled for `Version 86.0.4240.22` on `MacOS 64-bit`)
- `scraper.py` is the main image-finding script. It iterates through the targets, scrolls though Google Images, picks out and resolves the image URIs and then creates a task that is sent to the broker for pickup by the workers
- `targets.txt` is a file holding desired keywords
- `tasks.py` is the worker's scope. As designed, this is the only file accessible to the workers and so their `task`, i.e. downloading an image given a URI, is defined here

### Output
See the `images` folder generated after a quick run of the program

### Prerequisites
RabbitMQ should be running as:

```bash
➜  ~ rabbitmq-server
Configuring logger redirection

  ##  ##      RabbitMQ 3.8.9
  ##  ##
  ##########  Copyright (c) 2007-2020 VMware, Inc. or its affiliates.
  ######  ##
  ##########  Licensed under the MPL 2.0. Website: https://rabbitmq.com

  Doc guides: https://rabbitmq.com/documentation.html
  Support:    https://rabbitmq.com/contact.html
  Tutorials:  https://rabbitmq.com/getstarted.html
  Monitoring: https://rabbitmq.com/monitoring.html

  Logs: /usr/local/var/log/rabbitmq/rabbit@localhost.log
        /usr/local/var/log/rabbitmq/rabbit@localhost_upgrade.log

  Config file(s): (none)

  Starting broker... completed with 6 plugins.
```

Appropriate virtual_hosts, user, user_tag, and permissions should be set up

```bash
rabbitmqctl add_user buzz buzz
rabbitmqctl add_vhost buzz_vhost
rabbitmqctl set_user_tags buzz buzz_tag
rabbitmqctl set_permissions -p buzz_host buzz ".*" ".*" ".*"
```

Celery workers should be running as:

```bash
➜  buzz celery -A buzz_celery worker --loglevel=info

celery@Selwyn-Lloyds-MacBook-Pro-4827.local v5.0.1 (singularity)

macOS-10.14.6-x86_64-i386-64bit 2020-10-23 14:38:29

[config]
.> app:         buzz_celery:0x10ed5eeb0
.> transport:   amqp://buzz:**@localhost:5672/buzz_vhost
.> results:     rpc://
.> concurrency: 4 (prefork)
.> task events: OFF (enable -E to monitor tasks in this worker)

[queues]
.> celery           exchange=celery(direct) key=celery


[tasks]
  . buzz_celery.tasks.download_image

[2020-10-23 14:38:29,895: INFO/MainProcess] Connected to amqp://buzz:**@127.0.0.1:5672/buzz_vhost
[2020-10-23 14:38:29,973: INFO/MainProcess] mingle: searching for neighbors
[2020-10-23 14:38:31,114: INFO/MainProcess] mingle: all alone
[2020-10-23 14:38:31,140: INFO/MainProcess] celery@Selwyn-Lloyds-MacBook-Pro-4827.local ready.
```