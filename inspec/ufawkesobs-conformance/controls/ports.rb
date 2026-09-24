# AGENTS.md §4 / docs/ARCHITECTURE.md "Ports & Access" table: verifies the
# *actually running* container is bound the way compose.yaml declares --
# catches a container started before a port-binding change (e.g. #335's
# localhost restriction) that was never recreated with `--force-recreate`.

compose = YAML.load_file('/compose.yaml')

compose['services'].each do |name, svc|
  declared_ports = svc['ports'] || []
  next if declared_ports.empty?

  container_name = svc['container_name'] || name

  control "conformance-ports-#{name}" do
    impact 1.0
    title "#{name}: running container's bound ports match compose.yaml"

    only_if("#{container_name} is running") { docker_container(container_name).exist? }

    raw = command("docker inspect #{container_name} --format '{{json .NetworkSettings.Ports}}'").stdout
    actual = begin
      JSON.parse(raw)
    rescue JSON::ParserError
      {}
    end

    declared_ports.each do |mapping|
      parts = mapping.to_s.split(':')
      container_port = parts.pop
      host_port = parts.pop
      host_ip = parts.empty? ? '0.0.0.0' : parts.pop

      bindings = actual["#{container_port}/tcp"] || []
      found = bindings.any? { |b| b['HostPort'] == host_port && b['HostIp'] == host_ip }

      describe "#{name} port mapping #{mapping}" do
        subject { found }
        it { should eq true }
      end
    end
  end
end
