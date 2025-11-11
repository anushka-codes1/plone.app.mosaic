from plone.app.blocks.interfaces import CONTENT_LAYOUT_RESOURCE_NAME
from plone.app.blocks.interfaces import SITE_LAYOUT_RESOURCE_NAME
from plone.app.blocks.utils import resolveResource
from plone.app.mosaic.interfaces import IMosaicLayer
from plone.app.mosaic.utils import getPersistentResourceDirectory
from plone.base.interfaces import INonInstallable
from plone.resource.manifest import MANIFEST_FILENAME
from zope.component import getUtility
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory


EXAMPLE_SITE_LAYOUT = b"""\
[sitelayout]
title = Plone layout (Custom)
description = Example site layout
file = site.html
"""

EXAMPLE_CONTENT_LAYOUT = b"""\
[contentlayout]
title = Basic (Custom)
description = Example content layout
file = basic.html
"""


@implementer(INonInstallable)
class HiddenProfiles:
    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller"""
        return [
            # in any case we got an uninstall, here we hide it
            "plone.app.mosaic:uninstall",
            # and lets hide our dependencies as well.
            "plone.app.drafts:default",
            "plone.app.blocks:default",
            "plone.app.standardtiles:default",
            "plone.app.tiles:default",
            "plone.formwidget.querystring:default",
        ]


def post_handler(context):
    portal = context.portal_url.getPortalObject()
    create_ttw_layout_examples(portal)

    # If plone.app.discussion is not installed in the site, remove the
    # discussion tile entries from the registry so the "Discussion" tile
    # does not appear in the Mosaic Insert menu (Plone 6.1 makes
    # plone.app.discussion optional).
    try:
        qi = portal.portal_quickinstaller
    except Exception:
        qi = None

    if qi is None or not getattr(qi, "isProductInstalled", lambda name: False)(
        "plone.app.discussion"
    ):
        # remove registry records that belong to the discussion tile
        from plone.registry.interfaces import IRegistry
        from zope.component import getUtility

        registry = getUtility(IRegistry)
        prefix = "plone.app.mosaic.app_tiles.plone_app_standardtiles_discussion"
        for key in tuple(registry.records):
            if key.startswith(prefix):
                try:
                    del registry.records[key]
                except Exception:
                    # best-effort: continue if we cannot delete a key
                    continue


def create_ttw_site_layout_examples(portal):
    request = portal.REQUEST
    alsoProvides(request, IMosaicLayer)
    sitelayout = getPersistentResourceDirectory(SITE_LAYOUT_RESOURCE_NAME)
    custom = getPersistentResourceDirectory("custom", sitelayout)
    custom.writeFile(MANIFEST_FILENAME, EXAMPLE_SITE_LAYOUT)
    custom.writeFile(
        "site.html",
        resolveResource("++sitelayout++default/default.html").encode("utf-8"),
    )


def create_ttw_content_layout_examples(portal):
    request = portal.REQUEST
    alsoProvides(request, IMosaicLayer)
    contentlayout = getPersistentResourceDirectory(CONTENT_LAYOUT_RESOURCE_NAME)
    custom = getPersistentResourceDirectory("custom", contentlayout)
    custom.writeFile(MANIFEST_FILENAME, EXAMPLE_CONTENT_LAYOUT)
    custom.writeFile(
        "basic.html",
        resolveResource("++contentlayout++default/basic.html").encode("utf-8"),
    )


def create_ttw_layout_examples(portal):
    factory = getUtility(IVocabularyFactory, name="plone.availableSiteLayouts")
    vocab = factory(portal)
    if "++sitelayout++default/default.html" in vocab:
        create_ttw_site_layout_examples(portal)
    factory = getUtility(IVocabularyFactory, name="plone.availableContentLayouts")
    vocab = factory(portal)
    if "/++contentlayout++default/basic.html" in vocab:
        create_ttw_content_layout_examples(portal)
