import cache
import build


s="1.5.2 1.5.1 1.5.1-rc.1 1.5.0 1.5.0-rc.2 1.5.0-rc.1 1.4.4 1.4.3 1.4.2 1.4.1 1.4.1-rc.1 1.4.0 1.4.0-rc.1 1.3.1 1.3.1-rc.1 1.3.0-rc.1 1.2.1 1.2.1-rc.3 1.2.1-rc.2 1.2.1-rc.1 1.2.0-rc.1 1.2.0-beta.1 1.1.1 1.1.1-rc.1 1.1.0 1.1.0-rc.2 1.1.0-rc.1 1.0.1 1.0.1-rc.1 1.0.0 0.9.0 0.8.0-rc.27 0.8.0-rc.26 0.8.0-rc.25 0.8.0-rc.14 0.8.0-rc.12 0.8.0-rc.11 0.8.0-rc.10 0.7.0 0.6.4 0.6.3 0.5.5"

versions = s.split()

for version in versions[:5]:
	platforms = []
	for id in build.getSupportedPlatforms(version):
		platforms.append(build.platformConvert(id, "id", "name"))
	#print(platforms)

	for platform in platforms:
		print("configure", platform, version, "test")
		print("build", "test")
	
	
