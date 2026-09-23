# AGENTS.md §4: image versions must be pinned. compose.yaml pins every
# static image by digest so a `docker pull` under the same tag can never
# silently swap the running binary. This checks the *actually running*
# container was created from that exact image@sha256 reference, catching a
# stale container that predates a digest bump and was never recreated.
#
# Services built locally (`build:` instead of `image:` -- telemetry-generator,
# dora-api) have no pinned digest to compare against and are skipped.

compose = YAML.load_file('/compose.yaml')

compose['services'].each do |name, svc|
  next unless svc.key?('image')

  container_name = svc['container_name'] || name
  expected_image = svc['image']

  control "conformance-image-#{name}" do
    impact 1.0
    title "#{name}: running container was created from the pinned image digest"

    only_if("#{container_name} is running") { docker_container(container_name).exist? }

    describe command("docker inspect #{container_name} --format '{{.Config.Image}}'") do
      its('stdout.strip') { should cmp expected_image }
    end
  end
end
