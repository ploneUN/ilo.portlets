from zope.interface import Interface

from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form
from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone import PloneMessageFactory as _
from zope.annotation.interfaces import IAnnotations
from persistent.dict import PersistentDict
from Products.CMFCore.utils import getToolByName

from operator import itemgetter
from heapq import nlargest

from time import time

class Imissionreports(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    # TODO: Add any zope.schema fields here to capture portlet configuration
    # information. Alternatively, if there are no settings, leave this as an
    # empty interface - see also notes around the add form and edit form
    # below.

    # some_field = schema.TextLine(title=_(u"Some field"),
    #                              description=_(u"A field to use"),
    #                              required=True)


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(Imissionreports)

    path = "/intranet/reports/mission-reports/all-mission-reports"

    def __init__(self, path=None):

        self.path=path

    @property
    def title(self):
        return _(u"Statistics")


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('missionreports.pt')

    anno_key = 'ilo.portlets.cache'

    def __init(self, *args):
        context = aq_inner(self.context)
        portal_catalog = getToolByName(context, 'portal_catalog')

    def update_cache(self):
        anno = IAnnotations(self.context)
        anno.setdefault(self.anno_key, PersistentDict())
        cache = anno[self.anno_key]
        cache['total'] = self._total
        cache['international_count'] = self._international_count
        cache['domestic_count'] = self._domestic_count
        cache['themes'] = self._themes
        cache['themes_international'] = self._themes_international
        cache['themes_domestic'] = self._themes_domestic
        cache['domestic'] = self._domestic
        cache['international'] = self._international


    def cache(self):
        if self.request.get('force_cache_update', None):
            self.update_cache()
        anno = IAnnotations(self.context)
        anno.setdefault(self.anno_key, PersistentDict())
        cache = anno[self.anno_key]
        if not cache.has_key('total'):
            self.update_cache()
        return cache

    @property
    def _total(self):
        context = aq_inner(self.context)
        portal_catalog = getToolByName(context, 'portal_catalog')
            
        #grab all mission reports
        reports = portal_catalog.searchResults(portal_type='MissionReport',review_state='internally_published')

        return len(reports)

    @property
    def _international_count(self):
        context = aq_inner(self.context)
        portal_catalog = getToolByName(context, 'portal_catalog')
        reports = portal_catalog.searchResults(portal_type='MissionReport',
                review_state='internally_published',domestic='International')
        return len(reports)

    @property
    def _domestic_count(self):
        context = aq_inner(self.context)
        portal_catalog = getToolByName(context, 'portal_catalog')
        reports = portal_catalog.searchResults(portal_type='MissionReport',
                review_state='internally_published',domestic='Domestic')
        return len(reports)
        
    @property
    def _themes(self):
        context = aq_inner(self.context)
        portal_catalog = getToolByName(context, 'portal_catalog')
        
        #grab all mission reports
        reports = portal_catalog.searchResults(portal_type='MissionReport',review_state='internally_published')

        return self._top_three(reports)

    @property
    def _themes_international(self):

        context = aq_inner(self.context)
        portal_catalog = getToolByName(context, 'portal_catalog')
        
        #grab all mission reports
        reports = portal_catalog.searchResults(portal_type='MissionReport',review_state='internally_published',domestic='International')

        return self._top_three(reports)

    @property
    def _themes_domestic(self):

        context = aq_inner(self.context)
        portal_catalog = getToolByName(context, 'portal_catalog')
        
        #grab all mission reports
        reports = portal_catalog.searchResults(portal_type='MissionReport', 
                                               review_state='internally_published',
                                               domestic='Domestic')

        return self._top_three(reports)



    def _top_three(self, reports):
        #grab all available themes

        themes = []

        for o in reports:
            theme = o.getTheme
            for t in theme:
                if t != "Other":
                    themes.append(t)

        #We currently filter out Other until it's not top item after
        #adding new themes to MissionReports

        top = self.mostcommon(themes)

        theme1 = top[0]
        theme2 = top[1]
        theme3 = top[2]

        results = [theme1, theme2, theme3]

        return results


    @property
    def _domestic(self):

        context = aq_inner(self.context)
        portal_catalog = getToolByName(context, 'portal_catalog')
        
        #grab domestic mission reports
        reports = portal_catalog.searchResults(portal_type='MissionReport',review_state='internally_published',domestic='Domestic')
        
        #grab all available countries

        countries= []

        for o in reports:
            country = o.getMission_location
            for t in country:
               countries.append(t)

        top = self.mostcommon(countries)

        country1 = top[0]
        country2 = top[1]
        country3 = top[2]

        results = [country1,country2,country3]

        return results

    @property
    def _international(self):

        context = aq_inner(self.context)
        portal_catalog = getToolByName(context, 'portal_catalog')
        
        #grab domestic mission reports
        reports = portal_catalog.searchResults(portal_type='MissionReport',review_state='internally_published',domestic='International')
        
        #grab all available countries

        countries= []

        for o in reports:
            country = o.getMission_location
            for t in country:
               countries.append(t)
       
        top = self.mostcommon(countries)
   
        country1 = top[0]
        country2 = top[1]
        country3 = top[2]

        results = [country1,country2,country3]

        return results


    def mostcommon(self, iterable, n=None):
        """Return a sorted list of the most common to least common elements and
        their counts.  If n is specified, return only the n most common elements.
        """

        # http://code.activestate.com/recipes/347615/ (Raymond
        # Hettinger)
        
        bag = {}
        bag_get = bag.get
        for elem in iterable:
            bag[elem] = bag_get(elem, 0) + 1
        if n is None:
            return sorted(bag.iteritems(), key=itemgetter(1), reverse=True)
        it = enumerate(bag.iteritems())
        nl = nlargest(n, ((cnt, i, elem) for (i, (elem, cnt)) in it))
        return [(elem, cnt) for cnt, i, elem in nl]

# NOTE: If this portlet does not have any configurable parameters, you can
# inherit from NullAddForm and remove the form_fields variable.

class AddForm(base.NullAddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    #form_fields = form.Fields(Imissionreports)

    def create(self):
        return Assignment()

# NOTE: IF this portlet does not have any configurable parameters, you can
# remove this class definition and delete the editview attribute from the
# <plone:portlet /> registration in configure.zcml
