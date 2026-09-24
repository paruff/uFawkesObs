# AGENTS.md §4: "All services must have healthcheck: defined." The static
# check (tests/unit/test_compose_versions.py) only confirms the YAML key
# exists. This checks the *live* container actually reports healthy --
# catching a healthcheck that's declared but broken (wrong port, wrong path,
# binary missing after a base-image change).
#
# Services without a healthcheck: block in compose.yaml (otel-collector,
# tempo, alertmanager-discord -- all distroless with no health-query
# subcommand, documented inline in compose.yaml) are skipped automatically
# since this loop only acts on services that declare one.

compose = YAML.load_file('/compose.yaml')

compose['services'].each do |name, svc|
  next unless svc.key?('healthcheck')

  container_name = svc['container_name'] || name

  control "conformance-healthcheck-#{name}" do
    impact 1.0
    title "#{name}: running container reports a healthy healthcheck status"

    only_if("#{container_name} is running") { docker_container(container_name).exist? }

    describe command("docker inspect #{container_name} --format '{{.State.Health.Status}}'") do
      its('stdout.strip') { should cmp 'healthy' }
    end
  end
end
