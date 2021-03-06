# Automated tests for Automation Week UI challenges from MoT

This repo provides test automation code for Automation Week 2020 UI challenges (Ministry of Testing).
Different implementations and techniques are provided, showcasing how this could be achieved. Each has pros/cons that have to be considered.

Note: it's a learning exercise, so it may not be perfect. Nevertheless, I think it can be useful to get started.

## Overview of UI challenges

Next follows a description of the UI challenges for the sample website application [Restful Brooker Platform](https://automationintesting.online/) kindly provided by [Mark Winteringham](https://twitter.com/2bittester) / [Richard Bradshaw](https://twitter.com/FriendlyTester).

The tests are pretty simple and the purpose is to exercise test automation, refining the approach, be aware of some challenges, etc.

![](images/target_sut.jpg)

### Challenge 1: Beginner

_Create an automated test that completes the contact us form on the homepage, submits it, and asserts that the form was completed successfully._

### Challenge 2: Intermediate

_Create an automated test that reads a message on the admin side of the site._

_You’ll need to trigger a message in the first place, login as admin, open that specific message and validate its contents._

### Challenge 3: Advanced

_Create an automated test where a user successfully books a room from the homepage._

_You’ll have to click ‘Book this Room’, drag over dates you wish to book, complete the required information and submit the booking._

## Approach for implementing automated tests

In this repo, you'll find two different Python implementations for automated tests/checks:

- one using pytest
- another using Model-Based Testing (MBT), using AltWalker which in turn uses GraphWalker

Both make use of the Page Objects Model (POM) facilitated by the pypom library. As pages can have different sections/regions, we can abstract those precisely as classes inherited from the Region class. This will make code cleaner and more readable.

```python
class FrontPage(Page):
    """Interact with frontpage."""

    _admin_panel_locator = (By.LINK_TEXT, "Admin panel")

    class ContactForm(Region):

        _contact_form_name_locator = (By.ID, "name")
...
```

In both implementations, you'll see references to a faking data library. I've combined controlled randomization of data to provide greater coverage; this is especially valuable in the MBT implementation as the model can be exercised automatically "indefinitely" (to a certain point).

### Standard tests using pytest

This implementation is what I would call the traditional/common way of implementing automated tests.
Tests are implemented in the file [contact_form_pom_tests.py](contact_form_pom_tests.py), as seen in this example for the sucessful contact test.

```python
    def test_contact_form_successful(self):
        page = FrontPage(self.driver, BASE_URL)
        page.open()
        page.contact_form.wait_for_region_to_load()
        page.contact_form.fill_contact_data(name="sergio", email="sergio.freire@example.com", phone="+1234567890",
                                            subject="doubt", description="Can I book rooms up to 2 months ahead of time?")
        self.assertEqual(page.contact_form.contact_feedback_message,
                         f"Thanks for getting in touch sergio!\nWe'll get back to you about\ndoubt\nas soon as possible.")
```

In this case data was initially hard-coded. However, by using [faker](https://faker.readthedocs.io/en/master/) library we can create a [custom test data provider](tests/my_contact_provider.py) for the contact and our test method can be rewriten as:

```python
    def test_contact_form_successful(self):
        page = FrontPage(self.driver, BASE_URL)
        page.open()
        page.contact_form.wait_for_region_to_load()
        name = fake.valid_name()
        email = fake.valid_email()
        phone = fake.valid_phone()
        subject = fake.valid_subject()
        description = fake.valid_description()
        page.contact_form.fill_contact_data(
            name=name, email=email, phone=phone, subject=subject, description=description)
        self.assertEqual(page.contact_form.contact_feedback_message,
                         f"Thanks for getting in touch {name}!\nWe'll get back to you about\n{subject}\nas soon as possible.")
```

The first two challenges are solved in a similar way.

However, for the last challenge there are validations for the information provided to the user in the calendar about the total nights and the total price amount.
Besides checking the confirmation message displayed upon booking, also the persisted booking object is checked.
These checks are possible thanks to a basic implementation of a REST API client, that can obtain internal state of the stored data.


```python
   def test_book_successful(self):
        page = FrontPage(self.driver, BASE_URL)
        page.open()

        # click on first room
        room = page.rooms.available_rooms()[0]
        page.rooms.click_book_room(room)

        # book some nights, starting today
        today = date.today()
        start_date = today
        total_nights = 2
        end_date = today+timedelta(days=total_nights)
        page.rooms.select_calendar_dates(
            start_day=start_date.day, end_day=end_date.day)

        # check displayed information on the total nights and price, before submitting
        price_per_night = self.booker_api.get_rooms()[0]['roomPrice']
        total_price = price_per_night*total_nights
        page.rooms.select_calendar_dates(
            start_day=start_date.day, end_day=end_date.day)
        for selection_block in page.rooms.get_date_selection_blocks():
            self.assertEqual(selection_block.text,
                             f'{total_nights} night(s) - £{total_price}')

        # submit booking request
        start_date_str = start_date.isoformat()
        end_date_str = end_date.isoformat()
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = fake.valid_email()
        phone = fake.valid_phone()
        page.rooms.fill_booking_contact_data(
            first_name=first_name, last_name=last_name, email=email, phone=phone)
        page.rooms.click_submit_booking()

        # check confirmation message and stored booking on system
        last_booking = self.booker_api.get_bookings()[-1]
        self.assertEqual(page.rooms.booking_confirmed_message,
                         f"Booking Successful!\nCongratulations! Your booking has been confirmed for:\n{start_date_str} - {end_date_str}\nClose")
        self.assertTrue(last_booking['firstname'] == first_name and last_booking['lastname'] == last_name and last_booking['bookingdates']['checkin']
                        == start_date_str and last_booking['bookingdates']['checkout'] == end_date_str, f"booking not found (last_booking={last_booking}")
```

### Model-based tests using AltWalker and GraphWalker

With MBT, usually we have the model (either made using a visual model editor or from the IDE) and the underlying code.
In our case, models are stored in JSON format under the [models](models) directory.
The test code associated to vertices and egdges is implemented in the file [test.py](tests/test.py).

Using [Model Editor](https://altom.gitlab.io/altwalker/model-editor/) (or [GraphWalker Studio](https://graphwalker.github.io/)), we can model our application using a directed graph. In simple words, each vertex represents a state and each edge is a transition/action made in the application. Tests are made on the vertices/states.
Modeling is a challenge in itself and we can model the application and how we interact with it in different ways. Models are not exhaustive; they're a focused perspective on a certain behavior that we want to understand. MBT provides greater coverage and also a great way to visualize and discuss the application behavior/usage.

### Addressing challenge 1 with MBT

For the first challenge (i.e. contact form submission), we start from an initial state, from where we just have one possible action/edge: load the frontpage.
Then we can consider another state, where the frontpage is loaded and the contact form is available.
Two additional states are possible: one for a successful contact and another for an unsuccessful contact submission. We can go to these states by either submitting valid or invalid contact data.
One curious thing comes out from the model: after a successful contact, we can only make a new contact if we load/refresh the frontpage again. Was this an expected behavior? Well, we would have to discuss with the team.

![](images/mbt_contact_form.jpg)

With GraphWalker Studio we can run the model in offline and see the paths (sequence of vertices and edges) performed.

The code for each vertex and edge is quite simple as seen ahead.

Example of __e_submit_valid_contact_data__ code, showcasing usage of faker library:
```python

    def e_submit_valid_contact_data(self, data):
        page = FrontPage(self.driver, BASE_URL)
        page.contact_form.wait_for_region_to_load()

        name = fake.valid_name()
        email = fake.valid_email()
        phone = fake.valid_phone()
        subject = fake.valid_subject()
        description = fake.valid_description()

        data['global.last_contact_name'] = name
        data['global.last_contact_email'] = email
        data['global.last_contact_phone'] = phone
        data['global.last_contact_subject'] = subject
        data['global.last_contact_description'] = description

        page.contact_form.fill_contact_data(
            name=name, email=email, phone=phone, subject=subject, description=description)
```

Example of __v_contact_successful__ code:
```python
    def v_contact_successful(self, data):
        page = FrontPage(self.driver, BASE_URL)        
        name = data['last_contact_name']
        subject = data['last_contact_subject']
        self.assertEqual(page.contact_form.contact_feedback_message,
                         f"Thanks for getting in touch {name}!\nWe'll get back to you about\n{subject}\nas soon as possible.")
```


![](images/mbt_contact_form_offline.gif)

One can make this model a bit more detailed and complex, by making explicit edges/transitions for the process of submitting one field as invalid. This makes the graph harder to read though and it will only be relevant if we want to distinguish those cases.

![](images/mbt_contact_form_detailed.jpg)

### Addressing challenge 2 with MBT

In order to validate if the contact/message appears correctly in the admin page (2nd challenge), we start from a vertex/state related to a successful contact. This vertex has a shared state with the first model shared earlier, which allows AltWalker/GraphWalker to jump from one to the other.

We can then go to the admin panel, authenticate if needed, go to the inbox/messages section, open and check the details of the last contact message.
We can see several edges corresponding to actions that can be done, allowing us to transverse the graph and thus go to different application states.

Some edges (e.g. e_admin_correct_login) have "actions" defined in the model, to set an internal variable that can be useful later on.

Example:
```javacript
logged_in=true;
```

Some edges (e.g. **e_click_admin_panel**, from **v_contact_successful** to **v_admin_login**) have "guards", so they're only performed if those guard conditions are true.

Example:
```javacript
logged_in!=true
```

In this exercise, we take advantage of using model variables (e.g. last_contact_name, last_contact_subject) to temporarily store information about the last contact. The actual contact data used is implemented in code side and is populated on the model variables used for this purpose.

![](images/mbt_message_backoffice.jpg)

### Addressing challenge 3 with MBT

Challenge 3 (i.e. new booking) can also be addressed using a simple model, having a variable named *total_nights*, defined at model level, for controlling the intended number of nights to book.

![](images/mbt_new_booking1.jpg)

The previous model depicts a sequential set of actions and corresponding states, so it mimics a typical automated test as seen in the pytest implementation.
Even though feasible, and as there's only one path in the graph, this model doesn't provide exceptional value except that it turns visible our own model of the system.

_Note: another possible model could deal with the fact that the contact and date selection don't need to happen in sequence, and also provide the ability to jump back to the initial page. Well, many variations can be done depending on what we want to verify and the risks we have in mind._

![](images/mbt_new_booking2.jpg)

### Pre-requisites

- Python3
- Firefox (or other browser)
- GraphWalker v4.2.0 (v4.3.0 has some issues with AltWalker v0.2.7); see instructions [here](https://graphwalker.github.io/)

Install the python dependencies:

```pip install -r requirements.txt```

### Running automated tests

#### Standard tests using pytest

In order to run the standard pytest tests, just execute:
```pytest -s contact_form_pom_tests.py.py```

or, if you prefer using the helper bash script:

```./run_pytest.sh```

#### Model-based tests using AltWalker and GraphWalker

In order to run AltWalker tests (e.g. for the contact form) you need to define the [path generator and stop condition(s)](https://github.com/GraphWalker/graphwalker-project/wiki/Generators-and-stop-conditions). For example,

_random(vertex_coverage(100) and edge_coverage(100))_


... will use the "random" generator and will stop walking in the graph if all vertices and edges have been visited.
If we want, we can add additional conditions. For example, to keep running the tests until a certain amount of time has elapsed.

_random(vertex_coverage(100) and edge_coverage(100) and time_duration())_


To run the tests,and perform some initial consistency validations, just execute the following commands.

```bash

altwalker check -m models/contact_form.json "random(vertex_coverage(100) and edge_coverage(100))"
altwalker verify -m models/contact_form.json tests
altwalker online tests -m models/contact_form.json "random(vertex_coverage(100) and edge_coverage(100))"
```

If you prefer, you may also use the helper bash scripts:

```./run_altwalker_contact.sh```

```./run_altwalker_contact_detailed.sh```

```./run_altwalker_contact_with_message.sh```

```./run_altwalker_new_booking1.sh```

If you wish to run the tests against a specific URL instead of the default (https://aw1.automationintesting.online), you just need to define the BASE_URL environment variable.

```bash
BASE_URL="https://aw3.automationintesting.online" ./run_pytest.sh
```

## Configuration

The default configuration parameters are defined in [config.ini](config.ini). Some may be overridden by environment variables, if they exist.

## Final thoughts

On the app:

- app has some testability issues that inhibit usage of stable locators
- app has several bugs, intended or not :)

On the automated tests implementation:

- we can automate checks for the current behavior but we can't guarantee if that is the original intended one (e.g. phone format, fields size, flow behavior)
- randomization of data: control it, for reproduction purposes, using a seed
- Model-Based Testing:
  - can easily expose usage scenarios that go beyond happy paths
  - models can connect with one another through shared states, which is useful
  - can be combined with randomization of data to provide greater coverage
  - beware of managing data outside of the model (i.e. in the code) and in the model using variables
  - not used to replace traditional tests (happy path and negative tests)
  - can be harder to debug

## Room for improvement

These are some points that can be further improved, namely locators.
Others could include:

- ability to define browser (e.g. firefox, chrome, etc) to use
- ability to configure headless behavior

## References

- [AltWalker documentation](https://altom.gitlab.io/altwalker/altwalker/index.html)
- [Examples provided by AltWalker](https://altom.gitlab.io/altwalker/altwalker/examples.html)
- [GraphWalker and GraphWalker Studio](https://graphwalker.github.io/)
- Python packages
  - [pypom](https://pypom.readthedocs.io/en/latest/)
  - [webdriver](https://pypi.org/project/selenium/)
  - [faker](https://faker.readthedocs.io/en/master/)

## Contact

You can find me on [Twitter](https://twitter.com/darktelecom).

## LICENSE

[MIT](LICENSE).