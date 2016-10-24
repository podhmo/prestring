package models

type ArchiveFormat string

const (
	// Tarball : a member of ArchiveFormat
	Tarball ArchiveFormat = "tarball"
	// Zipball : a member of ArchiveFormat
	Zipball ArchiveFormat = "zipball"
)