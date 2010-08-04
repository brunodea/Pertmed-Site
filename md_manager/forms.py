from django import forms
from macros import informations

class ProfileForm(forms.Form):
    name = forms.CharField(max_length=30)

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)

        for item, fields in informations:
            for field in fields:
                self.fields[field + '_' + item] = forms.BooleanField(required=False, label=field)
    
        try:
            if not self.phone_list:
                pass
        except AttributeError:
            self.phone_list = []

    def update_phoneNumbers(self):
        for i in range(0, len(self.phone_list)):
            self.fields[self.phone_list[i].label] = self.phone_list[i]

    def add_phoneNumber(self, howmany=1):
        init = len(self.phone_list)
        for i in range(init, howmany + init):
            phone_number = forms.CharField(required=False, label='Phone_' + str(i), max_length=10)
            self.phone_list.append(phone_number)
        self.update_phoneNumbers()

    def __unicode__(self):
        return "Profile Form"








