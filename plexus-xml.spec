Name:		plexus-xml
Version:	4.0.0
Release:	1
Summary:	Plexus XML helpers, including Xpp3Dom
Group:		Development/Java
License:	Apache-2.0
URL:		https://github.com/codehaus-plexus/plexus-xml
# Tag plexus-xml-4.0.0. No prebuilt jars.
Source0:	%{name}-%{version}.tar.gz

BuildArch:	noarch
BuildRequires:	java-current-devel
BuildRequires:	sysjar
BuildRequires:	mvn(org.apache.maven:maven-api-meta)
BuildRequires:	mvn(org.apache.maven:maven-api-xml)
BuildRequires:	mvn(org.apache.maven:maven-xml-impl)
BuildRequires:	mvn(org.codehaus.plexus:plexus-utils)

%description
XML pull parser and Xpp3Dom from Plexus XML 4.0.0. Xpp3Dom in this
release is a view over Maven 4 XmlNodeImpl. Modello 2.1.2 reads
models through these classes when it generates the Maven 3.9.5
sources.

%prep
%autosetup -n %{name}-%{version} -p1
find . \( -name '*.jar' -o -name '*.class' -o -name '*.so' -o -name '*.node' -o -name '*.wasm' \) -delete

%build
set -eo pipefail
export JAVA_HOME=%{_jvmdir}/java-openjdk
export PATH="$JAVA_HOME/bin:$PATH"
META=%{_javadir}/maven-api-meta.jar
API=%{_javadir}/maven-api-xml.jar
IMPL=%{_javadir}/maven-xml-impl.jar
test -s "$META"
test -s "$API"
test -s "$IMPL"
find src/main/java -name '*.java' ! -name module-info.java > sources.list
test "$(wc -l < sources.list)" -eq 22
mkdir -p classes
javac --release 8 -encoding UTF-8 -Xlint:-options -proc:none \
	-cp "$META:$API:$IMPL" \
	-d classes @sources.list
jar cf plexus-xml.jar -C classes .
jar i plexus-xml.jar

cat > plexus-xml.pom << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.codehaus.plexus</groupId>
  <artifactId>plexus-xml</artifactId>
  <version>4.0.0</version>
  <name>Plexus XML Utilities</name>
  <description>Plexus XML 4.0.0, including Xpp3Dom.</description>
  <url>https://github.com/codehaus-plexus/plexus-xml</url>
  <licenses>
    <license>
      <name>Apache-2.0</name>
      <url>https://www.apache.org/licenses/LICENSE-2.0.txt</url>
    </license>
  </licenses>
  <dependencies>
    <dependency>
      <groupId>org.apache.maven</groupId>
      <artifactId>maven-xml-impl</artifactId>
      <version>4.0.0.alpha.5</version>
    </dependency>
    <dependency>
      <groupId>org.apache.maven</groupId>
      <artifactId>maven-api-xml</artifactId>
      <version>4.0.0.alpha.5</version>
    </dependency>
  </dependencies>
</project>
EOF

%install
set -eo pipefail
sysjar install --buildroot %{buildroot} \
	--artifact plexus-xml.pom:plexus-xml.jar \
	--file-name plexus-xml \
	--filelist .mfiles

%check
set -eo pipefail
export JAVA_HOME=%{_jvmdir}/java-openjdk
export PATH="$JAVA_HOME/bin:$PATH"
XML=%{buildroot}%{_javadir}/plexus-xml.jar
META=%{_javadir}/maven-api-meta.jar
API=%{_javadir}/maven-api-xml.jar
IMPL=%{_javadir}/maven-xml-impl.jar
UTILS=%{_javadir}/plexus-utils.jar
test -s "$XML"
mkdir -p check
cat > check/Smoke.java << 'EOF'
import org.codehaus.plexus.util.xml.Xpp3Dom;
import org.codehaus.plexus.util.xml.Xpp3DomBuilder;
import java.io.StringReader;
public class Smoke {
	public static void main(String[] args) throws Exception {
		Xpp3Dom dom = Xpp3DomBuilder.build(new StringReader(
			"<project><module>core</module></project>"));
		Xpp3Dom child = dom.getChild(0);
		System.out.println("pxml_ok " + dom.getName() + " " + child.getName() + " " + child.getValue());
	}
}
EOF
CP="$META:$API:$IMPL:$UTILS:$XML"
javac --release 8 -encoding UTF-8 -Xlint:-options -proc:none \
	-cp "$CP" -d check check/Smoke.java
java -cp "check:$CP" Smoke > check/out.txt
cat check/out.txt
grep -F -q 'pxml_ok project module core' check/out.txt

%files -f .mfiles
%license LICENSE.txt
%doc README.md NOTICE.txt
