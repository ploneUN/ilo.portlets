from collective.portlet.collectionmultiview.interfaces import ICollectionMultiViewBaseRenderer,ICollectionMultiViewRenderer
from zope.component import adapts
from zope.interface import implements
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from plone.memoize.instance import memoize
from Acquisition import aq_inner

class CollectionMultiViewBaseRenderer(object):
    adapts(ICollectionMultiViewBaseRenderer)
    implements(ICollectionMultiViewRenderer)

    def __init__(self, base):
        self.request = base.request
        self.context = aq_inner(base.context)
        self.data = base.data
        self.results = base.results
        self.collection_url = base.collection_url
        self.collection = base.collection
        self.base = base

    def render(self, *args, **kwargs):
        return self.template(*args, **kwargs)

    def tag(self, obj, scale='tile', css_class='tileImage'):
        context = aq_inner(obj)
        # test for leadImage and normal image
        for fieldname in ['leadImage','image']:
            field = context.getField(fieldname)
            if field is not None:
                if field.get_size(context) != 0:
                    return field.tag(context, scale=scale, css_class=css_class)
        return ''

class RecentRenderer(CollectionMultiViewBaseRenderer):

    __name__ = 'Recent Items Renderer'

    template = ViewPageTemplateFile('recent.pt')


class MissionReportRenderer(CollectionMultiViewBaseRenderer):

    __name__ = 'Mission Report Collection'

    template = ViewPageTemplateFile('mission-report-collection.pt')

class ILOEventRenderer(CollectionMultiViewBaseRenderer):

    __name__ = 'ILO Event Collection'

    template = ViewPageTemplateFile('events.pt')

