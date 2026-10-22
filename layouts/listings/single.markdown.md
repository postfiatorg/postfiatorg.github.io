{{- $base := strings.TrimSuffix "/" site.BaseURL -}}
{{- $inReview := eq .Params.status "in-review" -}}
# {{ .Title }}

{{ with .Params.summary }}> {{ . }}

{{ end -}}
{{ if $inReview -}}
Status: in review, placeholder. Expected source: {{ .Params.source_repo }} `{{ .Params.source_path }}`.
{{- else -}}
Mirror of {{ .Params.source_repo }} `{{ .Params.source_path }}` @ {{ .Params.source_commit }}{{ with .Params.source_branch }} ({{ . }}){{ end }}{{ if .Params.source_dirty }}, uncommitted draft{{ end }}.
Source: https://github.com/{{ .Params.source_repo }}/blob/{{ .Params.source_commit }}/{{ .Params.source_path }}
{{- end }}
Canonical: {{ .Permalink }}
Listings index: {{ $base }}/listings/index.md · JSON: {{ $base }}/listings/index.json · Agent guide: {{ $base }}/listings/agents.md

---

{{ replace (strings.TrimSpace .RawContent) "](/" (printf "](%s/" $base) }}
