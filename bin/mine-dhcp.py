#!/usr/bin/python
# vim: noet sw=4 ts=4

import	sys
import	os
import	pwd

class	Miner( object ):

	def	__init__( self, whoami = None ):
		self.hosts = dict()
		try:
			for host in os.listdir( 'hosts' ):
				with open( os.path.join( 'hosts', host ) ) as f:
					self.hosts[ host ] = f.readline().strip()
		except:
			pass
		if not whoami:
			whoami = os.getenv( 'SUDO_USER' )
			if whoami:
				self.uid = int( os.getenv( 'SUDO_UID' ) )
				self.gid = int( os.getenv( 'SUDO_GID' ) )
		if not whoami:
			whoami = os.getenv( 'USER' )
			pw_ent = pwd.getpwnam( whoami )
			self.uid = pw_ent.st_uid
			self.gid = pw_ent.st_gid
		return

	def	load( self, fn = '/etc/dhcp/dhcpd.conf' ):
		host = None
		with open( fn ) as f:
			for line in f:
				line = line.split( '#', 1 )[0]
				for c in [ ';', '{', '}' ]:
					line = line.replace( c, ' {0} '.format( c ) )
				tokens = map(
					str.strip,
					line.split()
				)
				L = len( tokens )
				if L == 3:
					if tokens[0] == 'host':
						host = tokens[ 1 ]
				elif L == 4:
					if tokens[0] == 'hardware' and tokens[1] == 'ethernet':
						if host:
							MAC = tokens[2].lower()
							self.hosts[ host ] = MAC
							host = None
		return

	def	export( self ):
		for host in sorted( self.hosts ):
			fn = os.path.join( 'systems', host )
			with open( fn, 'w' ) as f:
				print >>f, '{0}'.format( self.hosts[ host ] )
			os.chown( fn, self.uid, self.gid )
			stat = os.stat( fn )
			print '{0:03o}{1:03o} {2:07o} {3}'.format(
				stat.st_uid,
				stat.st_gid,
				stat.st_mode,
				fn
			)
		return

	def	report( self ):
		width = max(
			map(
				len,
				self.hosts
			)
		)
		fmt = '{{0:>{0}}} {{1}}'.format( width )
		for host in sorted( self.hosts ):
			print fmt.format( host, self.hosts[host] )
		return

if __name__ == '__main__':
	m = Miner()
	m.load()
	m.export()
	m.report()
	exit( 0 )
