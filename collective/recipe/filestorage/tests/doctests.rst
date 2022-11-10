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
   >>> print(system(join('bin', 'buildout') + ' -q'))

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

