# Web Link Checker

A Python script to recursively check links on a web page and their final URLs using Selenium and BeautifulSoup.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [License](#license)

## Overview

This script is designed to check links on a specified web page and log any issues related to the final URLs and HTTP status codes.

## Features

- Recursively checks links on a web page.
- Logs final URLs and HTTP status codes for each link.
- Configurable options for logging and depth of recursion.

## Installation

Clone the repository:

   ```bash
   git clone https://github.com/your-username/your-repository.git
   cd your-repository
   ```

## Configuration

You can configure the script using the config.json file. Customize the configuration according to your needs.

   ```bash
 {
    "site": "https://example.com",
    "log_to_console": true,
    "dir_logs": "logs",
    "date_format_filename": "%Y%m%d_%H%M%S",
    "date_format_log": "%Y-%m-%d %H:%M:%S",
    "log_format": "%(asctime)s [%(levelname)s] %(message)s"
}
```
