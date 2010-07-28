from django import forms
from macros import informations

class ProfileForm(forms.Form):
    name = forms.CharField(max_length=30)

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.form_list = []

        for item, fields in informations:
            self.fields[item] = forms.BooleanField(required=False, label=item)
            for field in fields:
                self.fields[field + '_' + item] = forms.BooleanField(required=False, label=field)

    def __unicode__(self):
        return "Profile Form"


