from faker import Faker
from faker.providers import BaseProvider


class MyContactProvider(BaseProvider):
    # name_size > 0
    # 11 <= message_size <= 21
    # 11 <= phone_size <= 21
    # 5 <= subject_size <= 100
    # 20 <= message_size <= 2000

    def text_less_than_or_greater_than(self, min_chars=0, max_chars=0):
        if self.generator.pyint(max_value=1) > 0:
            return self.generator.pystr(min_chars=0, max_chars=(min_chars-1))
        else:
            return self.generator.pystr(min_chars=(max_chars+1), max_chars=(max_chars*10))

    def valid_name(self):
        return self.generator.name()

    def invalid_name(self):
        return ''

    def valid_email(self):
        return self.generator.email()

    def invalid_email(self):
        return self.generator.name()

    def valid_phone(self):
        return self.random_number(digits=15, fix_len=True)

    def invalid_phone(self):
        # generate numbers of up to 9 digits
        return self.random_number(digits=None, fix_len=False)

    def valid_subject(self):
        subject = "doubt about bathroom"
        try_nr = 10
        while try_nr < 10:
            try_nr += 1
            subject = self.generator.sentence()
            if len(subject) >= 11 and len(subject) <= 21:
                break
        return subject

    def invalid_subject(self):
        return self.text_less_than_or_greater_than(min_chars=5, max_chars=100)

    def valid_description(self):
        description = "This is a sample doubt. I wonder if all rooms have a private bathroom?"
        try_nr = 10
        while try_nr < 10:
            try_nr += 1
            description = self.generator.sentence()
            if len(description) >= 20 and len(description) <= 20000:
                break
        return description

    def invalid_description(self):
        return self.generator.pystr(min_chars=0, max_chars=19)
