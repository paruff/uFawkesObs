# AGENTS.md §4: "Volumes for persistent data must be named, not anonymous."
# An anonymous volume (Docker-generated random name, no host path) makes
# data untraceable and easy to lose on container recreation. This asserts
# every mount on the running container is either a bind mount to a named
# host path or a Docker volume with an explicit name -- never an anonymous
# volume.

compose = YAML.load_file('/compose.yaml')

compose['services'].each do |name, svc|
  container_name = svc['container_name'] || name

  control "conformance-volumes-#{name}" do
    impact 1.0
    title "#{name}: no anonymous volumes on the running container"

    only_if("#{container_name} is running") { docker_container(container_name).exist? }

    raw = command("docker inspect #{container_name} --format '{{json .Mounts}}'").stdout
    mounts = begin
      JSON.parse(raw)
    rescue JSON::ParserError
      []
    end

    anonymous = mounts.select { |m| m['Type'] == 'volume' && m['Name'].to_s.empty? }

    describe "#{name} anonymous volume count" do
      subject { anonymous.length }
      it { should eq 0 }
    end
  end
end
