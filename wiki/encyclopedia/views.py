from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django import forms
from random import choice
from . import util
import markdown2

# A class to store input from the search bar
class NewTasksForm(forms.Form):
    form = forms.CharField(label="", widget=forms.TextInput(attrs={'class':'search', 'placeholder':'Search Encyclopedia'}))

# A class to store input from the new page form and later saved as markdown file
class NewPageForm(forms.Form):
    title = forms.CharField(label="Title", widget=forms.TextInput(attrs={'id':'title', 'placeholder':'Title', 'class':'form-control'}))
    content = forms.CharField(label="Content", widget=forms.Textarea(attrs={'id':'content', 'placeholder':'Content', 'class':'form-control', 'rows':'18'}))

# A class to store input from the edit page form    
class EditForm(forms.Form):
    content = forms.CharField(label="Content", widget=forms.Textarea(attrs={'id':'content', 'placeholder':'Content', 'class':'form-control', 'rows':'18'}))
    
search_form = NewTasksForm()

# Render index page with the current entries
def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "search_form": search_form
    })

# Display/render page for the requested entry
def title(request, title):
    #try renderring the requested entry
    try:
        return render(request, "encyclopedia/title.html",{
        "title": title,
        "content": markdown2.markdown(util.get_entry(title)),
        "search_form": search_form
        })
    #if the page doesn't exist or conclude a type error, render error message
    except TypeError:
        errmessage = "Requested page does not exist"
        return HttpResponseRedirect(reverse("error", kwargs={"message":errmessage}))

# Render edit page form
def edit(request, title):
    # User reached route via POST (as by submtting a from via POST)
    if request.method == "POST":
        # Retrieve input from form submitted by user
        edited_form = EditForm(request.POST)
        # Check validity
        if edited_form.is_valid():
            # 'Clean' the input
            edited_content = edited_form.cleaned_data["content"]
            # Save the content as a markdown file
            util.save_entry(title, edited_content)
            # Redirect to the edited page
            return HttpResponseRedirect(reverse("title", kwargs={"title":title}))
    # User reached route via GET
    else:
        # Retrieve and display the current content of the requested page
        entry_content = util.get_entry(title)
        edit_form = EditForm(initial={"content":entry_content})
        return render(request, "encyclopedia/edit.html", {
            "search_form": search_form,
            "title": title,
            "edit_form": edit_form
        })

# Application for the search bar
def search(request):
    if request.method == "POST":
        # Retrieve and display the current entries
        entries = util.list_entries()
        searched_form = NewTasksForm(request.POST)
        # Check validity
        if searched_form.is_valid():
            search = searched_form.cleaned_data["form"]
            # Check for matches in the entries list and display the matching page
            if search in entries:
                return HttpResponseRedirect(reverse("title", kwargs={"title":search}))
            else:
                results = []
                # Displays a list of all encyclopedia entries that have the query as a substring
                for entry in entries:
                    if search in entry:
                        results.append(entry)
                if len(results) > 0:
                    return render(request, "encyclopedia/search.html", {
                        "entries": results,
                        "search_form": search_form
                    })            
                # No matches!    
                else:
                    errmessage = "0 matches found!"
                    return HttpResponseRedirect(reverse("error", kwargs={"message":errmessage}))

# Render a page to submit a new page
def new(request):
    if request.method == "POST":
        # List all entries and retrieve from the input submitted
        entries = util.list_entries()
        new_page_form = NewPageForm(request.POST)
        # Check validity
        if new_page_form.is_valid():
            new_title = new_page_form.cleaned_data["title"]
            new_content = new_page_form.cleaned_data["content"]
            # Check for existing titles
            if new_title in entries:
                errmessage = "This title already exist, please provide another title."
                return HttpResponseRedirect(reverse("error", kwargs={"message":errmessage}))
            # If the title doesn't exist, save the new entry
            else:
                util.save_entry(new_title, new_content)
                return HttpResponseRedirect(reverse("title", kwargs={"title":new_title}))
    else:
        new_page_form = NewPageForm()
        return render(request, "encyclopedia/new.html", {
            "new_title_form": new_page_form["title"],
            "new_content_form": new_page_form["content"],
            "search_form": search_form
        })

# Random page application
def random(request):
    entries = util.list_entries()
    random_page = choice(entries)
    return HttpResponseRedirect(reverse("title", kwargs={"title":random_page}))

# Render an error page
def error(request, message):
    return render(request, "encyclopedia/error.html", {
        "search_form": search_form,
        "message": message
    })

