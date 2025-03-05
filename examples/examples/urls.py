from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import (
    include,
    path,
)

import examples.views as views
from examples import (
    experimental_examples,
    form_examples,
    menu_examples,
    page_examples,
    supernaut,
    table_examples,
)
from examples.main_menu import main_menu

urlpatterns = (
    [
        path('', views.IndexPage().as_view()),
        path('menu/', include(menu_examples)),
        path('iommi-admin/', include(views.ExampleAdmin.urls())),
        path('admin/', admin.site.urls),  # This is mostly to make the django_admin style available
        path('experimental/', include(experimental_examples)),
    ]
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    + main_menu.urlpatterns()
)
