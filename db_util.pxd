
from libcpp cimport bool
from libc.stdint cimport uint16_t
from libc.stdint cimport uint32_t

"""
DB is a cython wrapper class for fetch_lmdb.cpp / fetch_lmdb.h
"""

cdef extern from "tset.h" namespace "tset":
    cdef cppclass TSet:
        int tree_length
        TSet(int) except +
        void intersection_update(TSet *)
        void minus_update(TSet *)
        void union_update(TSet *)
        void add_item(int)
        bool has_item(int)
        void start_iteration()
        bool next_item(TSet *)
        char * get_data_as_char(int *)
        void deserialize(const void *)
        void erase()
        void set_length(int tree_length)
        void print_set()
        void copy(TSet *other)
    cdef cppclass TSetArray:
        void deserialize(const void *data, int size)
        void erase()
        void set_length(int tree_length)
        void print_array()
        void union_update(TSetArray *other)
        void intersection_update(TSetArray *other)
        void copy(TSetArray *other)

cdef extern from "tree_lmdb.h":
    cdef cppclass Tree:
        uint16_t zipped_tree_text_length
        char *zipped_tree_text
        void deserialize(void *serialized_data)
        int fill_sets(void **set_pointers, uint32_t *indices, unsigned char *set_types, unsigned char *optional, unsigned int count)
        int print_sets(void **set_pointers, unsigned char *set_types, unsigned int count)

cdef extern from "fetch_lmdb.h":
    cdef cppclass LMDB_Fetch:
        Tree *tree
        bool finished

        uint32_t* count
        uint32_t* tag_id

        uint32_t get_tag_id()
        uint32_t get_count()

        int open(const char *)
        void close()
        int begin_search(int ls, int la, uint32_t *lsets, uint32_t* larrays, uint32_t rarest)
        int get_next_fitting_tree()
        int get_id_for(char *key_data, int key_size)
        int get_count_for(uint32_t q_id)

cdef class DB:
    cdef LMDB_Fetch *thisptr
    cpdef open(self, solr_url)
    cpdef close(self)

    cpdef get_ids_from_solr(self,extras_dict, compulsory_items,solr)
    cpdef begin_search(self, extras_dict, compulsory_items, noncompulsory_items)
    cpdef int get_next_fitting_tree(self)
    
    cdef int fill_sets(self, void **set_pointers, uint32_t *indices, unsigned char *types, unsigned char *optional, int size)

    cdef bool finished(self)
    #def get_tree_text(self)

    cpdef uint32_t get_id_for(self, unicode key)
    cpdef uint32_t get_count_for(self, int idx)
    
cdef int TSET=1
cdef int TSETARRAY=2
