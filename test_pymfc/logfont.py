# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

import unittest

from pymfc.gdi import LogFont


class test_logfont(unittest.TestCase):
    def testCreate(self):
        lf = LogFont(height=1)
        self.failUnlessEqual(lf.height, 1)

        lf = LogFont(width=2)
        self.failUnlessEqual(lf.width, 2)
        
        lf = LogFont(escapement=3)
        self.failUnlessEqual(lf.escapement, 3)
        
        lf = LogFont(orientation=4)
        self.failUnlessEqual(lf.orientation, 4)
        
        lf = LogFont(weight=5)
        self.failUnlessEqual(lf.weight, 5)
        
        lf = LogFont(italic=6)
        self.failUnlessEqual(lf.italic, 6)
        
        lf = LogFont(underline=7)
        self.failUnlessEqual(lf.underline, 7)
        
        lf = LogFont(strikeout=8)
        self.failUnlessEqual(lf.strikeout, 8)

        lf = LogFont(facename=u"abc")
        self.failUnlessEqual(lf.facename, u"abc")

    def testCharSets(self):
        charsets = ['ansi_charset', 'baltic_charset', 'chinesebig5_charset', 
            'default_charset', 'easteurope_charset', 'gb2312_charset', 
            'greek_charset', 'hangul_charset', 'mac_charset', 'oem_charset', 
            'russian_charset', 'shiftjis_charset', 'symbol_charset', 
            'turkish_charset', 'johab_charset', 'hebrew_charset', 'arabic_charset', 
            'thai_charset',]
        
        lf = LogFont()
        for charset in charsets:
            setattr(lf, charset, True)
            self.failUnlessEqual(getattr(lf, charset), True)
            
            for other in charsets:
                if other == charset:
                    continue
                self.failUnlessEqual(getattr(lf, other), False)
                    
    def testOutPrecision (self):
        pres = ['out_character_precis',
                'out_default_precis',
                'out_device_precis',
                'out_outline_precis',
                'out_raster_precis',
                'out_string_precis',
                'out_stroke_precis',
                'out_tt_only_precis',
                'out_tt_precis']
        
        lf = LogFont()
        for pre in pres:
            setattr(lf, pre, True)
            self.failUnlessEqual(getattr(lf, pre), True)
            
            for other in pres:
                if other == pre:
                    continue
                self.failUnlessEqual(getattr(lf, other), False)
                    
    def testClipPrecision (self):
        pres = ['clip_default_precis',
                'clip_character_precis',
                'clip_stroke_precis',
                'clip_mask',
                'clip_embedded',
                'clip_lh_angles',
                'clip_tt_always',]
        
        lf = LogFont()
        for pre in pres:
            setattr(lf, pre, True)
            self.failUnlessEqual(getattr(lf, pre), True)
            
            for other in pres:
                if other == pre:
                    continue
                self.failUnlessEqual(getattr(lf, other), False)
                    
    def testQuality (self):
        qualities = ["default_quality",
            "draft_quality",
            "proof_quality"]
        
        lf = LogFont()
        for quality in qualities:
            setattr(lf, quality, True)
            self.failUnlessEqual(getattr(lf, quality), True)
            
            for other in qualities:
                if other == quality:
                    continue
                self.failUnlessEqual(getattr(lf, other), False)
                    

    def testPitchAndFamily (self):
        pitches = ["default_pitch",
            "fixed_pitch",
            "variable_pitch"]
        
        families = ["ff_decorative",
            "ff_dontcare",
            "ff_modern",
            "ff_roman",
            "ff_script",
            "ff_swiss"]


        lf = LogFont()
        for pitch in pitches:
            setattr(lf, pitch, True)
            self.failUnlessEqual(getattr(lf, pitch), True)
            
            for other in pitches:
                if other == pitch:
                    continue
                self.failUnlessEqual(getattr(lf, other), False)

            for f in families:
                setattr(lf, pitch, True)
                self.failUnlessEqual(getattr(lf, pitch), True)
                setattr(lf, pitch, False)
                self.failUnlessEqual(getattr(lf, pitch), True)
                
        for f in families:
            setattr(lf, f, True)
            self.failUnlessEqual(getattr(lf, f), True)
            
            for other in families:
                if other == f:
                    continue
                self.failUnlessEqual(getattr(lf, other), False)

            for pitch in pitches:
                setattr(lf, pitch, True)
                self.failUnlessEqual(getattr(lf, f), True)
                setattr(lf, pitch, False)
                self.failUnlessEqual(getattr(lf, f), True)

if __name__ == '__main__':
    unittest.main()

