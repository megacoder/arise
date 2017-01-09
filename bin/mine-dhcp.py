#!/usr/bin/python
# vim: noet sw=4 ts=4

import	sys
import	os
import	pwd
import	socket

class	Miner( object ):

	def	__init__( self, whoami = None ):
		self.host2mac = dict()
		self.mac2host = dict()
		if not whoami:
			whoami = os.getenv( 'SUDO_USER' )
			if whoami:
				self.uid = int( os.getenv( 'SUDO_UID' ) )
				self.gid = int( os.getenv( 'SUDO_GID' ) )
		if not whoami:
			whoami   = os.getenv( 'USER' )
			pw_ent   = pwd.getpwnam( whoami )
			self.uid = pw_ent.st_uid
			self.gid = pw_ent.st_gid
		return

	def	checkin_mac( self, host, mac ):
		if mac in self.mac2host and self.mac2host[mac] != host:
			print >>sys.stderr, 'MAC clash: {0:>32} {1:<32}'.format(
				self.mac2host[ mac ],
				host
			)
		else:
			self.mac2host[ mac ] = host
		self.host2mac[ host ] = mac
		return

	def	import_dhcpd( self, fn = '/etc/dhcp/dhcpd.conf' ):
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
							self.checkin_mac( host, MAC )
							host = None
		return

	def	import_leases( self, leases = '/var/lib/dhcpd/dhcpd.leases' ):
		host = None
		with open( leases ) as f:
			for line in f:
				line = line.replace( ';', '' )
				tokens = line.split( '#', 1 )[0].split()
				Ltokens = len( tokens )
				# print 'Ltokens={0}, tokens={1}'.format( Ltokens, tokens )
				if Ltokens and tokens[ 0 ] == 'lease':
					host_ip = tokens[ 1 ]
					try:
						(
							host, aliaslist, ipaddrlist
						) = socket.gethostbyaddr( host_ip )
					except:
						host = None
				elif Ltokens >= 3 and tokens[ 0 ] == 'hardware' and tokens[ 1 ] == 'ethernet':
					mac = tokens[ 2 ].lower()
					if host:
						self.checkin_mac( host, mac )
						host = None

	def	export( self ):
		width = max(
			map(
				len,
				self.host2mac
			)
		)
		fmt = '    {{0:>{0}s}} : "{{1}}",'.format( width + 2 )
		hosts_fn = os.path.join(
			os.path.dirname( __file__ ),
			'hosts.py'
		)
		with open( hosts_fn, 'w' ) as f:
			print >>f, 'hosts =\t{'
			for host in sorted( self.host2mac ):
				print >>f, fmt.format(
					'"{0}"'.format( host ),
					self.host2mac[ host ]
				)
			print >>f, '}'
		os.chmod( hosts_fn, 0644 )
		os.chown( hosts_fn, self.uid, self.gid )
		return

	def	report( self ):
		return

if __name__ == '__main__':
	m = Miner()
	m.import_dhcpd()
	m.import_leases()
	m.export()
	m.report()
	exit( 0 )
