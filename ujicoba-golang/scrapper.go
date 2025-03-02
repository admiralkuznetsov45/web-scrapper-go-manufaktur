package main

type dataAPDN struct {
	NamaPerusahaan    string `json:"nama_perusahaan"`
	KelompokJasa      string `json:"kelompok_jasa"`
	BidangJasa        string `json:"bidang_jasa"`
	Kemampuan         string `json:"kemampuan"`
	SubKemampuan      string `json:"sub_kemampuan"`
	NilaiKeberpihakan string `json:"nilai_keberpihakan"`
	StatusVerifikasi  string `json:"status_verifikasi"`
}
