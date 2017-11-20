import logging

import ckan.plugins as plugins
import domain_object
import package as _package
import resource
from package_extra import PackageExtra
from core import Revision
from group import Member
from tag import PackageTag

log = logging.getLogger(__name__)

__all__ = ['DomainObjectModificationExtension']

class DomainObjectModificationExtension(plugins.SingletonPlugin):
    """
    A domain object level interface to change notifications

    Triggered by all edits to table and related tables, which we filter
    out with check_real_change.
    """

    plugins.implements(plugins.ISession, inherit=True)

    def notify_observers(self, func):
        """
        Call func(observer) for all registered observers.

        :param func: Any callable, which will be called for each observer
        :returns: EXT_CONTINUE if no errors encountered, otherwise EXT_STOP
        """
        for observer in plugins.PluginImplementations(
                plugins.IDomainObjectModification):
            func(observer)


    def before_commit(self, session):
        self.notify_observers(session, self.notify)

    def after_commit(self, session):
        self.notify_observers(session, self.notify_after_commit)

    def notify_observers(self, session, method):
        session.flush()
        if not hasattr(session, '_object_cache'):
            return

        obj_cache = session._object_cache

        #send notification to celery queue only if obj_cache contains an object that does not belong to revision or package table, such as a harvest object
        contains_other_object = False
        for set_iterate, value in obj_cache.iteritems():
            for obj in value:
                if not isinstance(obj, (_package.Package, PackageTag, Revision, resource.Resource, PackageExtra, Member)):
                    contains_other_object = True

        if not contains_other_object:
            return

        new = obj_cache['new']
        changed = obj_cache['changed']
        deleted = obj_cache['deleted']

        for obj in set(new):
            if isinstance(obj, (_package.Package, resource.Resource)):
                method(obj, domain_object.DomainObjectOperation.new)
        for obj in set(deleted):
            if isinstance(obj, (_package.Package, resource.Resource)):
                method(obj, domain_object.DomainObjectOperation.deleted)
        for obj in set(changed):
            if isinstance(obj, resource.Resource):
                method(obj, domain_object.DomainObjectOperation.changed)
            if getattr(obj, 'url_changed', False):
                for item in plugins.PluginImplementations(plugins.IResourceUrlChange):
                    item.notify(obj)

        changed_pkgs = set(obj for obj in changed if isinstance(obj, _package.Package))

        for obj in new | changed | deleted:
            if not isinstance(obj, _package.Package):
                try:
                    related_packages = obj.related_packages()
                except AttributeError:
                    continue
                # this is needed to sort out vdm bug where pkg.as_dict does not
                # work when the package is deleted.
                for package in related_packages:
                    if package and package not in deleted | new:
                        changed_pkgs.add(package)
        for obj in changed_pkgs:
            method(obj, domain_object.DomainObjectOperation.changed)


    def notify(self, entity, operation):
        for observer in plugins.PluginImplementations(
                plugins.IDomainObjectModification):
            try:
                observer.notify(entity, operation)
            except Exception, ex:
                log.exception(ex)
                # We reraise all exceptions so they are obvious there
                # is something wrong
                raise

    def notify_after_commit(self, entity, operation):
        for observer in plugins.PluginImplementations(
                plugins.IDomainObjectModification):
            try:
                observer.notify_after_commit(entity, operation)
            except Exception, ex:
                log.exception(ex)
                # We reraise all exceptions so they are obvious there
                # is something wrong
                raise
