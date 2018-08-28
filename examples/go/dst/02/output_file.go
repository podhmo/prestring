package models

type ArchiveFormat string

const (
	Tarball ArchiveFormat = "tarball"
	Zipball ArchiveFormat = "zipball"
	// Tarball : a member of ArchiveFormat
	// Zipball : a member of ArchiveFormat
)