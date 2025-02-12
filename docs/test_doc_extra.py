from docs.models import Artist
from iommi import Form
from tests.helpers import req

request = req('get')


def test_extra_and_extra_evaluated():
    # language=rst
    """
    .. _extra:

    .. _extra_evaluated:

    `extra` and `extra_evaluated`
    =============================

    Very often it's useful to add some little bit of data on the side that you need
    later to customize something. We think it's important to support this use case
    with minimal amounts of code. To do this we have `extra` and `extra_evaluated`.
    This is your place to put whatever you want in order to extend iommi for a general
    feature or just some simple one-off customization for a single view.

    All `Part` derived classes have `extra` and `extra_evaluated` namespaces, for example:
    `Page`, `Column`, `Table`, `Field`, `Form`, and `Action`.

    You use `extra` to put some data you want as-is:

    """

    form = Form.create(
        auto__model=Artist,
        fields__name__extra__sounds_cool=True,
        extra__is_cool=True,
    )

    # @test
    form.bind(request=req('get'))
    # @end

    # language=rst
    """
    Here we add `sounds_cool` to the `name` field, and the `is_cool` value to the
    entire `Form`. We can then access these in e.g. a template:
    `{{ form.fields.name.extra.sounds_cool }}` and `{{ form.extra.is_cool }}`.

    `extra_evaluated` is useful when you want to use the iommi evaluation
    machinery to get some dynamic behavior:
    """

    form = Form.create(
        auto__model=Artist,
        fields__name__extra_evaluated__sounds_cool=lambda request, **_: request.user.is_staff,
        extra_evaluated__is_cool=lambda request, **_: request.user.is_staff,
    )

    # @test
    form.bind(request=req('get'))
    # @end

    # language=rst
    """
    These are accessed like this in the template: `{{ form.fields.name.extra_evaluated.sounds_cool }}`.
    """
