Example usage
=============

Let's create and run a minimal buildout that adds an extra filestorage::

   >>> write('buildout.cfg',
   ... '''
   ... [buildout]
   ... extends = base.cfg
   ... parts =
   ...     filestorage
   ...     instance
   ...
   ... [instance]
   ... recipe = plone.recipe.zope2instance
   ... user = me:pass
   ... # dead chicken .. if we don't specify no eggs, 'instance' is assumed
   ... # https://dev.plone.org/ticket/14023#comment:1
   ... eggs =
   ...
   ... [filestorage]
   ... recipe = collective.recipe.filestorage
   ... parts =
   ...     my-fs
   ... ''' % globals())
   >>> system(join('bin', 'buildout') + ' -q')

Our ``zope.conf`` should get the extra filestorage stanza automatically injected into it::

   >>> instance = os.path.join(sample_buildout, 'parts', 'instance')
   >>> with open(os.path.join(instance, 'etc', 'zope.conf'), 'r') as f:
   ...     print(f.read())
   %define INSTANCEHOME...instance
   ...
   <BLANKLINE>
   <zodb_db my-fs>
       cache-size 5000
       allow-implicit-cross-references false
       <filestorage >
         path .../var/filestorage/my-fs/my-fs.fs
       </filestorage>
       mount-point /my-fs
   </zodb_db>
   <BLANKLINE>

The recipe will also create a directory for the new filestorage::

    >>> 'my-fs' in os.listdir(os.path.join(sample_buildout, 'var', 'filestorage'))
    True

Let's make sure that the conf files will be regenerated whenever we make a change to a filestorage part,
even if the direct configuration for the zope/zeo parts hasn't changed::

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... extends = base.cfg
    ... parts =
    ...     filestorage
    ...     instance
    ...
    ... [instance]
    ... recipe = plone.recipe.zope2instance
    ... user = me:pass
    ... # dead chicken .. if we don't specify no eggs, 'instance' is assumed
    ... # https://dev.plone.org/ticket/14023#comment:1
    ... eggs =
    ...
    ... [filestorage]
    ... recipe = collective.recipe.filestorage
    ... parts =
    ...     my-fs
    ...     my-fs-2
    ... ''' % globals())
    >>> print(system(join('bin', 'buildout') + ' -q'))
    >>> with open('parts/instance/etc/zope.conf', 'r') as f:
    ...     'my-fs-2' in f.read()
    True

Let's make sure that the filestorage directory is not clobbered even if the filestorage part is removed
from the buildout::

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... extends = base.cfg
    ... parts =
    ...     instance
    ...
    ... [instance]
    ... recipe = plone.recipe.zope2instance
    ... user = me:pass
    ... eggs =
    ... ''' % globals())
    >>> print(system(join('bin', 'buildout') + ' -q'))
    >>> 'my-fs' in os.listdir(os.path.join(sample_buildout, 'var', 'filestorage'))
    True

We can override the defaults for a number of settings::

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... extends = base.cfg
    ... parts =
    ...     filestorage
    ...     instance
    ...
    ... [instance]
    ... recipe = plone.recipe.zope2instance
    ... user = me:pass
    ... eggs =
    ...
    ... [filestorage]
    ... recipe = collective.recipe.filestorage
    ... location = var/filestorage/%(fs_part_name)s/Data.fs
    ... blob-storage = var/blobstorage-%(fs_part_name)s
    ... zodb-name = %(fs_part_name)s_db
    ... zodb-cache-size = 1000
    ... zodb-mountpoint = /%(fs_part_name)s_mountpoint
    ... parts =
    ...     my-fs
    ... ''')
    >>> print(system(join('bin', 'buildout') + ' -q'))
    >>> instance = os.path.join(sample_buildout, 'parts', 'instance')
    >>> with open(os.path.join(instance, 'etc', 'zope.conf'), 'r') as f:
    ...     print(f.read())
    %define INSTANCEHOME...instance
    ...
    <BLANKLINE>
    <zodb_db my-fs_db>
        cache-size 1000
        allow-implicit-cross-references false
        <filestorage >
          path .../var/filestorage/my-fs/Data.fs
          blob-dir .../var/blobstorage-my-fs
        </filestorage>
        mount-point /my-fs_mountpoint
    </zodb_db>
    <BLANKLINE>

A setting can also be modified just for one particular filestorage, by creating a new part with
the ``filestorage_`` prefix, like so::

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... extends = base.cfg
    ... parts =
    ...     filestorage
    ...     instance
    ...
    ... [instance]
    ... recipe = plone.recipe.zope2instance
    ... user = me:pass
    ... eggs =
    ...
    ... [filestorage]
    ... recipe = collective.recipe.filestorage
    ... parts =
    ...     my-fs
    ...
    ... [filestorage_my-fs]
    ... zodb-cache-size = 1000
    ... ''' % globals())
    >>> print(system(join('bin', 'buildout') + ' -q'))
    >>> instance = os.path.join(sample_buildout, 'parts', 'instance')
    >>> with open(os.path.join(instance, 'etc', 'zope.conf'), 'r') as f:
    ...     print(f.read())
    %define INSTANCEHOME...instance
    ...
    <BLANKLINE>
    <zodb_db my-fs>
        cache-size 1000
        allow-implicit-cross-references false
        <filestorage >
          path .../var/filestorage/my-fs/my-fs.fs
        </filestorage>
        mount-point /my-fs
    </zodb_db>
    <BLANKLINE>


By default, the recipe adds the extra filestorages to each plone.recipe.zope2instance part in the buildout,
but you can tell it to only add it to certain parts::

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... extends = base.cfg
    ... parts =
    ...     filestorage
    ...     instance1
    ...     instance2
    ...
    ... [instance1]
    ... recipe = plone.recipe.zope2instance
    ... user = me:pass
    ... eggs =
    ...
    ... [instance2]
    ... recipe = plone.recipe.zope2instance
    ... user = me:pass
    ... eggs =
    ...
    ... [filestorage]
    ... recipe = collective.recipe.filestorage
    ... zopes = instance1
    ... parts =
    ...     my-fs
    ... ''' % globals())
    >>> print(system(join('bin', 'buildout') + ' -q'))
    >>> with open('parts/instance1/etc/zope.conf', 'r') as f:
    ...     'my-fs' in f.read()
    True
    >>> with open('parts/instance2/etc/zope.conf', 'r') as f:
    ...     'my-fs' in f.read()
    False

Example Usage with ZEO
======================

Here is a minimal buildout including a ZEO server and two ZODB clients::

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... extends = base.cfg
    ... parts =
    ...     filestorage
    ...     zeoserver
    ...     primary
    ...     secondary
    ...
    ... [zeoserver]
    ... recipe = plone.recipe.zeoserver
    ...
    ... [primary]
    ... recipe = plone.recipe.zope2instance
    ... user = me:pass
    ... zeo-client = 1
    ... eggs =
    ...
    ... [secondary]
    ... recipe = plone.recipe.zope2instance
    ... user = me:pass
    ... eggs =
    ... zeo-client = 1
    ...
    ... [filestorage]
    ... recipe = collective.recipe.filestorage
    ... parts =
    ...     my-fs
    ... ''' % globals())
    >>> print(system(join('bin', 'buildout') + ' -q'))
    Created directory .../parts/zeoserver
    Created directory .../parts/zeoserver/etc
    Created directory .../parts/zeoserver/var
    Created directory .../parts/zeoserver/log
    Created directory .../parts/zeoserver/bin
    Wrote file .../parts/zeoserver/etc/zeo.conf
    Wrote file .../parts/zeoserver/bin/zeoctl
    Changed mode for .../parts/zeoserver/bin/zeoctl to ...
    Wrote file .../parts/zeoserver/bin/runzeo
    Changed mode for .../parts/zeoserver/bin/runzeo to ...

This should result in the appropriate additions to ``zeo.conf`` and both ``zope.conf``'s::

    >>> zeoserver = os.path.join(sample_buildout, 'parts', 'zeoserver')
    >>> with open(os.path.join(zeoserver, 'etc', 'zeo.conf'), 'r') as f:
    ...     print(f.read())
    %define INSTANCE /sample-buildout/parts/zeoserver
    ...
    <BLANKLINE>
        <filestorage my-fs>
          path /sample-buildout/var/filestorage/my-fs/my-fs.fs
        </filestorage>
    <BLANKLINE>

    >>> primary = os.path.join(sample_buildout, 'parts', 'primary')
    >>> with open(os.path.join(primary, 'etc', 'zope.conf'), 'r') as f:
    ...     print(f.read())
    %define INSTANCEHOME /sample-buildout/parts/primary
    ...
    <BLANKLINE>
    <zodb_db my-fs>
     cache-size 5000
     allow-implicit-cross-references false
     <zeoclient>
       server 8100
       storage my-fs
       name my-fs_zeostorage
       var /sample-buildout/parts/primary/var
       cache-size 30MB
    <BLANKLINE>
     </zeoclient>
     mount-point /my-fs
    </zodb_db>
    <BLANKLINE>

    >>> secondary = os.path.join(sample_buildout, 'parts', 'secondary')
    >>> with open(os.path.join(secondary, 'etc', 'zope.conf'), 'r') as f:
    ...     print(f.read())
    %define INSTANCEHOME /sample-buildout/parts/secondary
    ...
    <BLANKLINE>
    <zodb_db my-fs>
     cache-size 5000
     allow-implicit-cross-references false
     <zeoclient>
       server 8100
       storage my-fs
       name my-fs_zeostorage
       var /sample-buildout/parts/secondary/var
       cache-size 30MB
    <BLANKLINE>
     </zeoclient>
     mount-point /my-fs
    </zodb_db>
    <BLANKLINE>

As above, we can override a number of the default parameters::

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... extends = base.cfg
    ... parts =
    ...     filestorage
    ...     zeoserver
    ...     primary
    ...     secondary
    ...
    ... [zeoserver]
    ... recipe = plone.recipe.zeoserver
    ...
    ... [primary]
    ... recipe = plone.recipe.zope2instance
    ... user = me:pass
    ... zeo-client = 1
    ... eggs =
    ...
    ... [secondary]
    ... recipe = plone.recipe.zope2instance
    ... user = me:pass
    ... zeo-client = 1
    ... eggs =
    ...
    ... [filestorage]
    ... recipe = collective.recipe.filestorage
    ... location = var/filestorage/%(fs_part_name)s/Data.fs
    ... blob-storage = var/blobstorage-%(fs_part_name)s
    ... zodb-cache-size = 1000
    ... zodb-name = %(fs_part_name)s_db
    ... zodb-mountpoint = /%(fs_part_name)s_mountpoint
    ... zeo-address = 8101
    ... zeo-client-cache-size = 50MB
    ... zeo-storage = %(fs_part_name)s_storage
    ... zeo-client-name = %(fs_part_name)s_zeostorage_name
    ... parts =
    ...     my-fs
    ... ''')
    >>> print(system(join('bin', 'buildout') + ' -q'))
    Created directory .../parts/zeoserver
    Created directory .../parts/zeoserver/etc
    Created directory .../parts/zeoserver/var
    Created directory .../parts/zeoserver/log
    Created directory .../parts/zeoserver/bin
    Wrote file .../parts/zeoserver/etc/zeo.conf
    Wrote file .../parts/zeoserver/bin/zeoctl
    Changed mode for .../parts/zeoserver/bin/zeoctl to ...
    Wrote file .../parts/zeoserver/bin/runzeo
    Changed mode for .../parts/zeoserver/bin/runzeo to ...
    <BLANKLINE>
    >>> zeoserver = os.path.join(sample_buildout, 'parts', 'zeoserver')
    >>> with open(os.path.join(zeoserver, 'etc', 'zeo.conf'), 'r') as f:
    ...     print(f.read())
    %define INSTANCE /sample-buildout/parts/zeoserver
    ...
    <BLANKLINE>
        <filestorage my-fs_storage>
          path /sample-buildout/var/filestorage/my-fs/Data.fs
          blob-dir /sample-buildout/var/blobstorage-my-fs
        </filestorage>
    <BLANKLINE>
    >>> primary = os.path.join(sample_buildout, 'parts', 'primary')
    >>> with open(os.path.join(primary, 'etc', 'zope.conf'), 'r') as f:
    ...     print(f.read())
    %define INSTANCEHOME /sample-buildout/parts/primary
    ...
    <BLANKLINE>
    <zodb_db my-fs_db>
     cache-size 1000
     allow-implicit-cross-references false
     <zeoclient>
       blob-dir /sample-buildout/var/blobstorage-my-fs
       shared-blob-dir on
       server 8101
       storage my-fs_storage
       name my-fs_zeostorage_name
       var /sample-buildout/parts/primary/var
       cache-size 50MB
    <BLANKLINE>
     </zeoclient>
     mount-point /my-fs_mountpoint
    </zodb_db>
    <BLANKLINE>
    >>> secondary = os.path.join(sample_buildout, 'parts', 'secondary')
    >>> with open(os.path.join(secondary, 'etc', 'zope.conf'), 'r') as f:
    ...     print(f.read())
    %define INSTANCEHOME /sample-buildout/parts/secondary
    ...
    <BLANKLINE>
    <zodb_db my-fs_db>
     cache-size 1000
     allow-implicit-cross-references false
     <zeoclient>
       blob-dir /sample-buildout/var/blobstorage-my-fs
       shared-blob-dir on
       server 8101
       storage my-fs_storage
       name my-fs_zeostorage_name
       var /sample-buildout/parts/secondary/var
       cache-size 50MB
    <BLANKLINE>
     </zeoclient>
     mount-point /my-fs_mountpoint
    </zodb_db>
    <BLANKLINE>

By default, the recipe adds the extra filestorages to the first
``plone.recipe.zeoserver`` part in the buildout, and will throw an error if
there is more than one part using this recipe.  However, you can override this
behavior by specifying a particular ZEO part.  In this case, the filestorages
will only be added to the Zopes using that ZEO, by default::

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... extends = base.cfg
    ... parts =
    ...     filestorage
    ...     zeoserver1
    ...     zeoserver2
    ...     primary
    ...     secondary
    ...     other-zope
    ...
    ... [zeoserver1]
    ... recipe = plone.recipe.zeoserver
    ... zeo-address = 8100
    ...
    ... [zeoserver2]
    ... recipe = plone.recipe.zeoserver
    ... zeo-address = 8101
    ...
    ... [primary]
    ... recipe = plone.recipe.zope2instance
    ... user = me:pass
    ... zeo-client = 1
    ... zeo-address = 8101
    ... eggs =
    ...
    ... [secondary]
    ... recipe = plone.recipe.zope2instance
    ... user = me:pass
    ... zeo-client = 1
    ... zeo-address = 8101
    ... eggs =
    ...
    ... [other-zope]
    ... recipe = plone.recipe.zope2instance
    ... user = me:pass
    ... zeo-client = 1
    ... zeo-address = 8100
    ... eggs =
    ...
    ... [filestorage]
    ... recipe = collective.recipe.filestorage
    ... zeo = zeoserver2
    ... parts =
    ...     my-fs
    ... ''' % globals())
    >>> print(system(join('bin', 'buildout') + ' -q'))
    Created directory .../parts/zeoserver2
    Created directory .../parts/zeoserver2/etc
    Created directory .../parts/zeoserver2/var
    Created directory .../parts/zeoserver2/log
    Created directory .../parts/zeoserver2/bin
    Wrote file .../parts/zeoserver2/etc/zeo.conf
    Wrote file .../parts/zeoserver2/bin/zeoctl
    Changed mode for .../parts/zeoserver2/bin/zeoctl to ...
    Wrote file .../parts/zeoserver2/bin/runzeo
    Changed mode for .../parts/zeoserver2/bin/runzeo to ...
    Created directory .../parts/zeoserver1
    Created directory .../parts/zeoserver1/etc
    Created directory .../parts/zeoserver1/var
    Created directory .../parts/zeoserver1/log
    Created directory .../parts/zeoserver1/bin
    Wrote file .../parts/zeoserver1/etc/zeo.conf
    Wrote file .../parts/zeoserver1/bin/zeoctl
    Changed mode for .../parts/zeoserver1/bin/zeoctl to ...
    Wrote file .../parts/zeoserver1/bin/runzeo
    Changed mode for .../parts/zeoserver1/bin/runzeo to ...
    <BLANKLINE>
    >>> with open('parts/zeoserver2/etc/zeo.conf', 'r') as f:
    ...     'my-fs' in f.read()
    True
    >>> with open('parts/zeoserver1/etc/zeo.conf', 'r') as f:
    ...     'my-fs' in f.read()
    False
    >>> with open('parts/primary/etc/zope.conf', 'r') as f:
    ...     'my-fs' in f.read()
    True
    >>> with open('parts/other-zope/etc/zope.conf', 'r') as f:
    ...     'my-fs' in f.read()
    False

Backup integration
==================

Backup integration::

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... extends = base.cfg
    ... parts =
    ...     filestorage
    ...     instance
    ...     backup
    ...
    ... [instance]
    ... recipe = plone.recipe.zope2instance
    ... user = me:pass
    ... eggs =
    ...
    ... [backup]
    ... recipe = collective.recipe.backup>=2.7
    ...
    ... [filestorage]
    ... recipe = collective.recipe.filestorage
    ... parts =
    ...     foo
    ...     bar
    ... backup = backup
    ... ''')
    >>> print(system(join('bin', 'buildout') + ' -q'))
    >>> with open('bin/backup', 'r') as f:
    ...     print(re.search(
    ...     r"storages\s*=\s*\[([^\]]+)\]",
    ...     f.read(),
    ...     flags=re.M).group(1))
    {'backup_location': '/sample-buildout/var/backups_foo',
      'blobdir': '',
      'datafs': '/sample-buildout/var/filestorage/foo/foo.fs',
      'snapshot_location': '/sample-buildout/var/snapshotbackups_foo',
      'storage': 'foo',
      'zip_location': '/sample-buildout/var/zipbackups_foo'},
     {'backup_location': '/sample-buildout/var/backups_bar',
      'blobdir': '',
      'datafs': '/sample-buildout/var/filestorage/bar/bar.fs',
      'snapshot_location': '/sample-buildout/var/snapshotbackups_bar',
      'storage': 'bar',
      'zip_location': '/sample-buildout/var/zipbackups_bar'},
     {'backup_location': '/sample-buildout/var/backups',
      'blob_backup_location': '/sample-buildout/var/blobstoragebackups',
      'blob_snapshot_location': '/sample-buildout/var/blobstoragesnapshots',
      'blob_zip_location': '/sample-buildout/var/blobstoragezips',
      'blobdir': '/sample-buildout/var/blobstorage',
      'datafs': '/sample-buildout/var/filestorage/Data.fs',
      'snapshot_location': '/sample-buildout/var/snapshotbackups',
      'storage': '1',
      'zip_location': '/sample-buildout/var/zipbackups'}

Backup with blob storage and custom filestorage location::

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... extends = base.cfg
    ... parts =
    ...     filestorage
    ...     instance
    ...     backup
    ...
    ... [instance]
    ... recipe = plone.recipe.zope2instance
    ... user = me:pass
    ... eggs =
    ...
    ... [backup]
    ... recipe = collective.recipe.backup>=2.7
    ...
    ... [filestorage]
    ... recipe = collective.recipe.filestorage
    ... location = var/filestorage/%(fs_part_name)s/Data.fs
    ... blob-storage = var/blobstorage-%(fs_part_name)s
    ... zodb-name = %(fs_part_name)s_db
    ... parts =
    ...     foo
    ...     bar
    ... backup = backup
    ... ''')
    >>> print(system(join('bin', 'buildout') + ' -q'))
    >>> with open('bin/backup', 'r') as f:
    ...     print(re.search(
    ...     r"storages\s*=\s*\[([^\]]+)\]",
    ...     f.read(),
    ...     flags=re.M).group(1))
    {'backup_location': '/sample-buildout/var/backups_foo',
      'blob_backup_location': '/sample-buildout/var/blobstoragebackups_foo',
      'blob_snapshot_location': '/sample-buildout/var/blobstoragesnapshots_foo',
      'blob_zip_location': '/sample-buildout/var/blobstoragezips_foo',
      'blobdir': '/sample-buildout/var/blobstorage-foo',
      'datafs': '/sample-buildout/var/filestorage/foo/Data.fs',
      'snapshot_location': '/sample-buildout/var/snapshotbackups_foo',
      'storage': 'foo',
      'zip_location': '/sample-buildout/var/zipbackups_foo'},
     {'backup_location': '/sample-buildout/var/backups_bar',
      'blob_backup_location': '/sample-buildout/var/blobstoragebackups_bar',
      'blob_snapshot_location': '/sample-buildout/var/blobstoragesnapshots_bar',
      'blob_zip_location': '/sample-buildout/var/blobstoragezips_bar',
      'blobdir': '/sample-buildout/var/blobstorage-bar',
      'datafs': '/sample-buildout/var/filestorage/bar/Data.fs',
      'snapshot_location': '/sample-buildout/var/snapshotbackups_bar',
      'storage': 'bar',
      'zip_location': '/sample-buildout/var/zipbackups_bar'},
     {'backup_location': '/sample-buildout/var/backups',
      'blob_backup_location': '/sample-buildout/var/blobstoragebackups',
      'blob_snapshot_location': '/sample-buildout/var/blobstoragesnapshots',
      'blob_zip_location': '/sample-buildout/var/blobstoragezips',
      'blobdir': '/sample-buildout/var/blobstorage',
      'datafs': '/sample-buildout/var/filestorage/Data.fs',
      'snapshot_location': '/sample-buildout/var/snapshotbackups',
      'storage': '1',
      'zip_location': '/sample-buildout/var/zipbackups'}

No backup integration::

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... extends = base.cfg
    ... parts =
    ...     filestorage
    ...     instance
    ...     backup
    ...
    ... [instance]
    ... recipe = plone.recipe.zope2instance
    ... user = me:pass
    ... eggs =
    ...
    ... [backup]
    ... recipe = collective.recipe.backup>=2.7
    ... additional_filestorages =
    ...     lorem
    ...     ipsum
    ...
    ... [filestorage]
    ... recipe = collective.recipe.filestorage
    ... parts =
    ...     foo
    ...     bar
    ... ''')
    >>> print(system(join('bin', 'buildout') + ' -q'))
    >>> with open('bin/backup', 'r') as f:
    ...     'lorem' in f.read()
    True
    >>> with open('bin/backup', 'r') as f:
    ...     'ipsum' in f.read()
    True
    >>> with open('bin/backup', 'r') as f:
    ...     'foo' in f.read()
    False
    >>> with open('bin/backup', 'r') as f:
    ...     'bar' in f.read()
    False


Error conditions
================

Important note: You must place all parts using the
collective.recipe.filestorage recipe before the part for the instances and
zeoservers that you are adding the filestorage to.  Otherwise you'll get an
error::

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... extends = base.cfg
    ... parts =
    ...     instance
    ...     filestorage
    ...
    ... [instance]
    ... recipe = plone.recipe.zope2instance
    ... user = me:pass
    ... eggs =
    ...
    ... [filestorage]
    ... recipe = collective.recipe.filestorage
    ... parts =
    ...     my-fs
    ... ''' % globals())
    >>> print(system(join('bin', 'buildout') + ' -q'))
    While:
    ...
    Error: [collective.recipe.filestorage] The "filestorage" part must be listed before the following parts in ${buildout:parts}: instance
    <BLANKLINE>

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... extends = base.cfg
    ... parts =
    ...     backup
    ...     filestorage
    ...     instance
    ...
    ... [instance]
    ... recipe = plone.recipe.zope2instance
    ... user = me:pass
    ... eggs =
    ...
    ... [backup]
    ... recipe = collective.recipe.backup>=2.7
    ...
    ... [filestorage]
    ... recipe = collective.recipe.filestorage
    ... parts =
    ...     my-fs
    ... backup = backup
    ... ''' % globals())
    >>> print(system(join('bin', 'buildout') + ' -q'))
    While:
    ...
    Error: [collective.recipe.filestorage] The "filestorage" part must be listed before the following parts in ${buildout:parts}: instance, backup
    <BLANKLINE>

Buildouts with multiple zeoserver parts will result in an
error if the desired ZEO to associate with is not explicitly specified::

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... extends = base.cfg
    ... parts =
    ...     filestorage
    ...     zeoserver1
    ...     zeoserver2
    ...     primary
    ...     secondary
    ...
    ... [zeoserver1]
    ... recipe = plone.recipe.zeoserver
    ...
    ... [zeoserver2]
    ... recipe = plone.recipe.zeoserver
    ...
    ... [primary]
    ... recipe = plone.recipe.zope2instance
    ... user = me:pass
    ... zeo-client = 1
    ... eggs =
    ...
    ... [secondary]
    ... recipe = plone.recipe.zope2instance
    ... user = me:pass
    ... zeo-client = 1
    ... eggs =
    ...
    ... [filestorage]
    ... recipe = collective.recipe.filestorage
    ... parts =
    ...     my-fs
    ... ''' % globals())
    >>> print(system(join('bin', 'buildout') + ' -q'))
    While:
    ...
    Error: [collective.recipe.filestorage] "filestorage" part found multiple zeoserver parts; please specify which one to use with the "zeo" option.

Specifying a nonexistent ZEO should result in an error::

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... extends = base.cfg
    ... parts =
    ...     filestorage
    ...     zeoserver
    ...     primary
    ...
    ... [zeoserver]
    ... recipe = plone.recipe.zeoserver
    ...
    ... [primary]
    ... recipe = plone.recipe.zope2instance
    ... user = me:pass
    ... zeo-client = 1
    ... eggs =
    ...
    ... [filestorage]
    ... recipe = collective.recipe.filestorage
    ... zeo = foobar
    ... parts =
    ...     my-fs
    ... ''' % globals())
    >>> print(system(join('bin', 'buildout') + ' -q'))
    While:
    ...
    Error: [collective.recipe.filestorage] "filestorage" part specifies nonexistant zeo part "foobar".

Specifying a nonexistent backup part should result in an error::

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... extends = base.cfg
    ... parts =
    ...     backup
    ...     filestorage
    ...     instance
    ...
    ... [instance]
    ... recipe = plone.recipe.zope2instance
    ... user = me:pass
    ... eggs =
    ...
    ... [backup]
    ... recipe = collective.recipe.backup>=2.7
    ...
    ... [filestorage]
    ... recipe = collective.recipe.filestorage
    ... parts =
    ...     my-fs
    ... backup = foobar
    ... ''')
    >>> print(system(join('bin', 'buildout') + ' -q'))
    While:
    ...
    Error: [collective.recipe.filestorage] "filestorage" part specifies nonexistant backup part "foobar".

So should specifying a nonexistent Zope part::

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... extends = base.cfg
    ... parts =
    ...     filestorage
    ...     zeoserver
    ...     primary
    ...
    ... [zeoserver]
    ... recipe = plone.recipe.zeoserver
    ...
    ... [primary]
    ... recipe = plone.recipe.zope2instance
    ... user = me:pass
    ... zeo-client = 1
    ... eggs =
    ...
    ... [filestorage]
    ... recipe = collective.recipe.filestorage
    ... zopes = foobar
    ... parts =
    ...     my-fs
    ... ''' % globals())
    >>> print(system(join('bin', 'buildout') + ' -q'))
    While:
    ...
    Error: [collective.recipe.filestorage] The "filestorage" part expected but failed to find the following parts in ${buildout:parts}: foobar

If the Zope/ZEO parts are being automatically identified, let's make sure
that we don't accidentally "wake up" parts that would not otherwise be
included in the buildout::

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... extends = base.cfg
    ... parts =
    ...     filestorage
    ...     instance
    ...
    ... [instance]
    ... recipe = plone.recipe.zope2instance
    ... user = me:pass
    ... eggs =
    ...
    ... [filestorage]
    ... recipe = collective.recipe.filestorage
    ... parts =
    ...     my-fs
    ...
    ... [foobar]
    ... recipe = plone.recipe.distros
    ... urls =
    ... ''' % globals())
    >>> print(system(join('bin', 'buildout') + ' -q'))
    >>> 'foobar' in os.listdir(os.path.join(sample_buildout, 'parts'))
    False
