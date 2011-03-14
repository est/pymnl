#!/usr/bin/python
# tests/attributes.py -- test interface for netlink message attributes
# Copyright 2011 Sean Robinson <seankrobinson@gmail.com>
#
# This file is part of the pymnl package, a Python interface
# for netlink sockets.
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public License
#  as published by the Free Software Foundation; either version 2.1 of
#  the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
#  USA
#

from random import randint
import unittest

import pymnl
from pymnl.attributes import *

class TestAttributes(unittest.TestCase):

    def _test_integer_constructor(self, const_, max_value_):
        """ Test the specified integer constructor.

            const_ - Attr constructor to test

            max_value_ - maximum value the integer can hold
        """
        for type_ in (TYPE_U8, TYPE_U16, TYPE_U32, TYPE_U64):
            # valid values
            random_ = randint(1, max_value_ - 1)
            for value_ in (0, random_, max_value_):
                self.assertTrue(isinstance(const_(type_, value_), Attr),
                                        "test value did not make an Attr")
            # invalid values
            random_ = randint(-1 * (max_value_ - 1), -2)
            for value_ in (-1, random_, -1 * max_value_, "test string"):
                self.assertRaises(TypeError, const_, type_, value_)

    def _test_integer_length(self, const_, max_value_, aligned_len_):
        """ Test the specified integer length.

            const_ - Attr constructor

            max_value_ - maximum value the integer can hold

            aligned_len_ - length of Attr value aligned to NLA size (in
                bytes); this value should not include the attribute header
        """
        for type_ in (TYPE_U8, TYPE_U16, TYPE_U32, TYPE_U64):
            random_ = randint(1, max_value_ - 1)
            for value_ in (0, random_, max_value_):
                one_attr = const_(type_, value_)
                # valid values
                self.assertEqual(len(one_attr), ATTR_HDRLEN + aligned_len_,
                            "length does not match expected Attr length")
                # invalid values
                self.assertNotEqual(len(const_(type_, value_)),
                            ATTR_HDRLEN + randint(0, aligned_len_ - 1),
                            "length unexpectedly matches")

    def _test_type(self, const_, value_):
        """ Test the Attr type.

            const_ - Attr constructor

            value_ - value for the Attr
        """
        # valid values
        for type_ in (TYPE_U8, TYPE_U16, TYPE_U32, TYPE_U64,
                                         TYPE_STRING, TYPE_NUL_STRING):
            one_attr = const_(type_, value_)
            self.assertEqual(one_attr.get_type(), type_,
                                    "returned type did not match")
            self.assertTrue(one_attr.type_valid(), "invalid type")
        # invalid values
        one_attr = const_(TYPE_MAX + 1, value_)
        self.assertFalse(one_attr.type_valid(), "unexpectedly valid type")

    def _test_integer_return(self, const_, get_method_, max_value_):
        """ Test an Attr.get_*() method.
        """
        for type_ in (TYPE_U8, TYPE_U16, TYPE_U32, TYPE_U64):
            # valid values
            random_ = randint(1, max_value_ - 1)
            for value_ in (0, random_, max_value_):
                one_attr = const_(type_, value_)
                self.assertEqual(get_method_(one_attr), value_,
                            "returned value does not match entered value")

    def _test_get_binary(self, const_, type_, value_, expected_value_):
        """ Test Attr.get_binary() method.
        """
        one_attr = const_(type_, value_)
        self.assertEqual(one_attr.get_binary(), expected_value_,
                    "binary value does not match expected value")

    def test_u8(self):
        """ Test one byte long Attr objects.
        """
        max_value_ = pow(2, 8) - 1
        self._test_integer_constructor(Attr.new_u8, max_value_)
        self._test_integer_length(Attr.new_u8, max_value_, 4)
        self._test_type(Attr.new_u8, 0)
        self._test_integer_return(Attr.new_u8, Attr.get_u8, max_value_)
        self._test_get_binary(Attr.new_u8, TYPE_U8, max_value_,
                                b'\x08\x00\x01\x00\xff\x00\x00\x00')

    def test_u16(self):
        """ Test two byte long Attr objects.
        """
        max_value_ = pow(2, 16) - 1
        self._test_integer_constructor(Attr.new_u16, max_value_)
        self._test_integer_length(Attr.new_u16, max_value_, 4)
        self._test_type(Attr.new_u16, 0)
        self._test_integer_return(Attr.new_u16, Attr.get_u16, max_value_)
        self._test_get_binary(Attr.new_u16, TYPE_U16, max_value_,
                                b'\x08\x00\x02\x00\xff\xff\x00\x00')

    def test_u32(self):
        """ Test four byte long Attr objects.
        """
        max_value_ = pow(2, 32) - 1
        self._test_integer_constructor(Attr.new_u32, max_value_)
        self._test_integer_length(Attr.new_u32, max_value_, 4)
        self._test_type(Attr.new_u32, 0)
        self._test_integer_return(Attr.new_u32, Attr.get_u32, max_value_)
        self._test_get_binary(Attr.new_u32, TYPE_U32, max_value_,
                                b'\x08\x00\x03\x00\xff\xff\xff\xff')

    def test_u64(self):
        """ Test eight byte long Attr objects.
        """
        max_value_ = pow(2, 64) - 1
        self._test_integer_constructor(Attr.new_u64, max_value_)
        self._test_integer_length(Attr.new_u64, max_value_, 8)
        self._test_type(Attr.new_u64, 0)
        self._test_integer_return(Attr.new_u64, Attr.get_u64, max_value_)
        self._test_get_binary(Attr.new_u64, TYPE_U64, max_value_,
                        b'\x0c\x00\x04\x00\xff\xff\xff\xff\xff\xff\xff\xff')

    def test_strnz(self):
        """ Test string value Attr objects.
        """
        for type_ in (TYPE_U8, TYPE_STRING):
            # valid values
            for test_string_ in (b'test string', b'nl80211', b'spam'):
                aligned_len_ = NLA_ALIGN(len(test_string_))
                strnz_ = Attr.new_strnz(type_, test_string_)
                self.assertTrue(isinstance(strnz_, Attr),
                                        "test string did not make an Attr")
                self.assertEqual(len(strnz_), (ATTR_HDRLEN + aligned_len_),
                                        "test string is wrong length")
                self.assertEqual(strnz_.get_str(), test_string_,
                            "returned value does not match entered value")
                self.assertEqual(strnz_.get_str_stripped(), test_string_,
                            "returned value does not match entered value")
            # invalid values
            random_ints_ = []
            for i_ in range(3): random_ints_.append(randint(-1000, 1000))
            for value_ in (random_ints_):
                self.assertRaises(TypeError, Attr.new_strnz, type_, value_)
        # other tests
        self._test_type(Attr.new_strnz, b'test')
        self._test_get_binary(Attr.new_strnz, TYPE_STRING, b'spam',
                                                b'\x08\x00\x05\x00spam')

    def test_strz(self):
        """ Test null-terminated string value Attr objects.
        """
        for type_ in (TYPE_U8, TYPE_NUL_STRING):
            # valid values
            for test_string_ in (b'test string', b'nl80211', b'spam'):
                aligned_len_ = NLA_ALIGN(len(test_string_) + 1)
                strz_ = Attr.new_strz(type_, test_string_)
                self.assertTrue(isinstance(strz_, Attr),
                                        "test string did not make an Attr")
                self.assertEqual(len(strz_), (ATTR_HDRLEN + aligned_len_),
                                        "test string is wrong length")
                self.assertEqual(strz_.get_str(), test_string_ + b'\x00',
                            "returned value does not match entered value")
                self.assertEqual(strz_.get_str_stripped(), test_string_,
                            "returned value does not match entered value")
            # invalid values
            random_ints_ = []
            for i_ in range(3): random_ints_.append(randint(-1000, 1000))
            for value_ in (random_ints_):
                self.assertRaises(TypeError, Attr.new_strz, type_, value_)
        # other tests
        self._test_type(Attr.new_strz, b'test')
        self._test_get_binary(Attr.new_strz, TYPE_NUL_STRING, b'spam',
                                b'\x0c\x00\n\x00spam\x00\x00\x00\x00')

    def test_nested(self):
        """ Test nested flag toggle and check.
        """
        one_attr = Attr.new_u8(TYPE_U8, 0)
        self.assertFalse(one_attr.is_nested(),
                    "nested flag should not be set in new Attr objects")
        one_attr.toggle_nested()
        self.assertTrue(one_attr.is_nested(),
                                            "nested flag should be set")
        one_attr.toggle_nested()
        self.assertFalse(one_attr.is_nested(),
                                        "nested flag should not be set")

    @staticmethod
    def suite():
        return unittest.TestLoader().loadTestsFromTestCase(TestAttributes)


class TestAttrParser(unittest.TestCase):

    def test_init_no_data(self):
        """ Test AttrParser object creation without data.
        """
        attr_parser = AttrParser()
        self.assertTrue(isinstance(attr_parser, AttrParser))

    def test_init_with_data(self):
        """ Test AttrParser object creation with data.
        """
        # manually create a TYPE_U16 attribute
        one_attr = Attr.new_u16(TYPE_U16, 4881)
        attr_parser = AttrParser(one_attr)
        self.assertTrue(isinstance(attr_parser, AttrParser))

    def test_parse_string(self):
        """ Test AttrParser.parse_string().
        """
        # no test, yet
        pass

    def test_parse(self):
        """ Test AttrParser.parse().
        """
        # manually create a TYPE_U16 attribute
        one_attr = Attr.new_u16(TYPE_U16, 4881)
        # create AttrParser without any data, yet
        attr_parser = AttrParser()
        # ask the parser to parse the test Attr
        attr_list = attr_parser.parse(one_attr)
        self.assertEqual(one_attr.get_binary(), attr_list[0].get_binary())

    def test_parse_nested(self):
        """ Test AttrParser.parse_nested().
        """
        # no test, yet
        pass

    def test_get_attrs(self):
        """ Test AttrParser.get_attrs().
        """
        # manually create a TYPE_U16 attribute
        one_attr = Attr.new_u16(TYPE_U16, 4881)
        # create AttrParser object using the test Attr
        attr_parser = AttrParser(one_attr)
        attr_list = attr_parser.get_attrs()
        self.assertEqual(one_attr.get_binary(), attr_list[0].get_binary())

    @staticmethod
    def suite():
        return unittest.TestLoader().loadTestsFromTestCase(TestAttrParser)

