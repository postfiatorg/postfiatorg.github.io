{{- $base := strings.TrimSuffix "/" site.BaseURL -}}
{{- $repo := .Params.repo | default "postfiatorg/postfiatl1v2" -}}
{{- $ref := .Params.design_docs_ref | default "main" -}}
{{- $gh := printf "https://github.com/%s/blob/%s/" $repo $ref -}}
{{- $abs := printf "](%s/" $base -}}
# {{ .Params.heading | default .Title }}

> {{ .Params.summary }}

Canonical: {{ .Permalink }}
JSON index: {{ $base }}/listings/index.json
Agent guide: {{ $base }}/listings/agents.md
Status as of: {{ .Lastmod.Format "2006-01-02" }}

{{ replace .RawContent "](/" $abs | strings.TrimSpace }}

**Status, plainly.** {{ .Params.honesty }}

## For the Coinbase listing team

{{ range .Params.cards -}}
{{- $p := site.GetPage .page -}}
- [{{ .title }}]({{ with $p }}{{ .Permalink }}{{ else }}{{ $base }}{{ .page }}/{{ end }}){{ if and $p (eq $p.Params.status "in-review") }} (in review){{ end }}: {{ .text }}{{ with $p }}{{ with .OutputFormats.Get "markdown" }} Markdown: {{ .Permalink }}{{ end }}{{ end }}
{{ end }}
## Status

| Area | State | Detail |
| --- | --- | --- |
{{ range .Params.status -}}
| {{ .area }} | {{ .state }} | {{ replace .detail "](gh:" (printf "](%s" $gh) }} |
{{ end }}
## Key design documents

Primary sources in https://github.com/{{ $repo }}, linked at `{{ $ref }}`{{ with .Params.design_docs_checked_commit }} (paths checked at {{ . }}){{ end }}.

{{ range .Params.design_docs -}}
- [{{ .title }}]({{ $gh }}{{ .path }}) (`{{ .path }}`, {{ .group }}): {{ .summary }}
{{ end }}
## For AI agents

{{ .Params.agents_intro }}

{{ range .Params.agents -}}
- {{ $base }}{{ .path }} ({{ .format }}): {{ .text }}
{{ end }}
## Contact

{{ replace .Params.contact "](gh:" (printf "](%s" $gh) }}
