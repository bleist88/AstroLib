"""
This file contains functions which are designed to read and write ascii files
to and from numpy record arrays.  The typical text file might look somethin
like:

    ##  This is a comment at the top of the file.
    #<  col_1           int32
    #<  col_2           float32
    #<  col_3           float32
    #<  col_4           U20
    1       3.14159         2.71828         Feynman
    2       2.71828         3.14159         Jefferson
    ##  Here is another comment randomly in the file.
    3       3.14159         2.71828         Beethoven
"""

from ._imports import *

##  ========================================================================  ##
##  Column Data

def read( file_name, dtype=None ):
    """
    This function reads an ascii file and returns a numpy record array.  If the
    dtype of the ascii data is not specified ( default ), the format of the data
    is specified by a header.  The typical text file might look somethin like:

        ##  This is a comment at the top of the file.
        #<  col_1           int32
        #<  col_2           float32
        #<  col_3           float32
        #<  col_4           U20
        1       3.14159         2.71828         Feynman
        2       2.71828         3.14159         Jefferson
        ##  Here is another comment randomly in the file.
        3       3.13159         2.71828         Beethoven

    Parameters:
        file_name       - str
            name of ascii file
        dtype           - dict
            numpy dtype or numpy like dtype dictionary

    Returns:
        array           - numpy record array
    """

    ## Retrieve body of text and the dtype a text file.

    body, comments, fdtype   = io.parse_file( file_name )

    if dtype is None:
        dtype   = fdtype

    ## Create an array and fill it with text.

    array       = np.zeros( len(body), dtype=dtype )
    bad_lines   = 0

    for i in range(len( body )):

        ## Write line to array if possible.

        try:
            array[i]    = tuple( body[i] )

        except:
            bad_lines += 1

    ## Inform user to lines that were not written.

    if bad_lines > 0:
        print( "%i lines not read in %s." % (bad_lines, file_name) )

    return array

##  ========================================================================  ##

def write(
    file_name, array, header=True, space=3,
    sci=False, ipad=6, fpad=8.6, spad=32,
    keep=False
):
    """
    This function writes an ascii data file from given numpy record array with a
    formatted header written from the dtype of the array.  The file will contain
    a header which looks like:

        #<   col_name_1          int32
        #<   col_name_2          float32
        #<   col_name_3          U27

    Parameters:
        file_name   - str
            name of ascii file
        array       - ndarray
            numpy ndarray to write
        header      - bool
            to write header to the file or not
        space       - int
            number of spaces between columns
        sci         - bool
            hack to use scientific notation for floats
        ipad        - int
            format for integers
        fpad        - float
            format for floats
        spad        - int
            format for strings ( currently pretty lame )
    """

    out_file    = open( file_name, "w" )

    ## Determine line format from array.

    dstring     = io.get_dstring(
        array.dtype, space=space, sci=sci, ipad=ipad, fpad=fpad, spad=spad
    )

    ##  I'd like to write this rather than using io.get_dstring() above.  This
    ##  is intended so that we can straighten up the gaps between columns.
    ##
    ##  1.  turn each column to string
    ##  2.  find max length of each column
    ##  3.  format including knowledge of max length

    ## Write header to file.

    if header is True:

        for name in list( array.dtype.names ):

            out_file.write( "#<  " + name )
            out_file.write( (25-len(name)) * " " )
            out_file.write( str(array.dtype[name]) )
            out_file.write( "\n" )

    ## Write formatted lines to file and close.

    for i in range(len( array )):

        out_file.write( dstring % tuple(array[i]) )
        out_file.write( "\n" )

    ##  If keep is True, return the file stream.
    ##  Also return the dstring for consistent writing.
    ##  Otherwise, close the file stream.

    if keep is True:
        out_file.flush()
        return  out_file, dstring
    else:
        out_file.close()

##  ========================================================================  ##

def add_column( original, col_name, col_format, data=None, after=None ):
    """
    This function adds a column to an existing numpy record array and returns
    the result.

    Parameters:
        original        - numpy array
            original numpy record array
        col_name        - str
            column name
        col_format      - str
            column format
        data            - new column array
            data to add

    Returns:
        numpy record array
    """

    ##  If after == None, place the column in the -1th position.

    if after is None or after == -1:

        new_dtype = {
            "names":    [
                original.dtype.names[i] for i in range( len(original.dtype) )
            ],
            "formats":  [
                original.dtype[i]       for i in range( len(original.dtype) )
            ]
        }

        new_dtype["names"].append( col_name )
        new_dtype["formats"].append( col_format )

    ##  If after == 0, place the column in the 0th position.

    if after == 0 or after == "0":

        new_dtype = { "names": [col_name], "formats": [col_format] }

        for col in original.dtype.names:

            new_dtype["names"].append( col )
            new_dtype["formats"].append( original.dtype[col] )

    ##  Otherwise, put the new column after the column specified by after.

    new_dtype   = { "names": [], "formats": [] }

    found       = False

    for i in range( len(original.dtype) ):

        new_dtype["names"].append( original.dtype.names[i] )
        new_dtype["formats"].append( original.dtype[i] )

        if original.dtype.names[i] == after:
            found   = True
            new_dtype["names"].append( col_name )
            new_dtype["formats"].append( col_format )

    if found is False:
        new_dtype["names"].append( col_name )
        new_dtype["formats"].append( col_format )

    ##  Declare the new array.

    new_array = np.zeros( original.size, dtype=new_dtype )

    for col in original.dtype.names:

        new_array[col] = original[col]

    if data is not None:

        new_array[col_name] = data

    return new_array

##  ========================================================================  ##

def start_file( file_name, array ):

    out_file    = open( file_name, "w" )

    for name in list( array.dtype.names ):

        out_file.write( "#<  " + name )
        out_file.write( (25-len(name)) * " " )
        out_file.write( str(array.dtype[name]) )
        out_file.write( "\n" )

def write_to( out_file, dstring, row_data ):

    out_file.write( dstring % tuple(row_data) )
    out_file.write( "\n" )
    out_file.flush()

##  ========================================================================  ##
##  ========================================================================  ##
##  Configuration Files

def read_configs( configs_file ):
    """
    Returns an ordered dictionary of variables defined in a .cfg file.
    """

    body    = io.get_body( configs_file )
    configs = collections.OrderedDict()

    ##  Create a placeholder [] for each key.   This must be done in advanced so
    ##  that if a key appears more than once, the values are simply appended to
    ##  the orginal.

    for i in range( len(body) ):
        configs[ body[i][0] ]   = []

    ##  Parse values.

    for i in range( len(body) ):

        ##  Create a list of values from the remainder of the line.
        ##  Split this via any comma separators.

        key     = body[i][0]
        values  = "".join( body[i][1:] ).split( "," )

        ##  Typset each value in values.  This accepts:
        ##      float, int, string, True, False, and None

        for j in range( len(values) ):

            if values[j].lower() == "true":
                values[j] = True

            elif values[j].lower() == "false":
                values[j] = False

            elif values[j].lower() == "none":
                values[j] = None

            else:
                try:
                    if "." in values[j]:
                        values[j] = float( values[j] )
                    else:
                        values[j] = int( values[j] )
                except:
                    values[j] = str( values[j] )

        ##  Add the key and the values to the dictionary.

        for value in values:
            configs[ key ].append( value )

    ##  If any values lists contain only 1 item, make the value singular.

    for key in configs:
        if len( configs[ key ] ) == 1:
            configs[ key ]  = configs[ key ][0]

    ##  Return.

    return configs

##  ========================================================================  ##

def write_configs( file_name, configs, comment=None ):
    """
    Write a configurations file from a configurations dictionary.
    """

    ##  Open file and write comment.

    out_file    = open( file_name, "w" )

    if comment is not None:
        out_file.write( "##  " + comment + "\n\n" )

    else:
        out_file.write( "\n\n" )

    ##  Create value strings from values.

    for key in configs:

        if isinstance( configs[key], (list, tuple) ):

            vals  = []

            for val in configs[key]:
                vals.append( str(val) )

            configs[key]    = ", ".join( vals )

    ##  Write configs to file.

    for key in configs:

        out_file.write( "%-28s  %s\n" % (key, configs[key]) )

    out_file.write("")
    out_file.close()

##  ========================================================================  ##
##  numpy formats
#
# DATA_TYPE       DESCRIPTION
#
# S             Byte-String
# U             Unicode Literal
# bool_	        Boolean (True or False) stored as a byte
# int_	        Default integer type (same as C long; normally either int64
#                   or int32)
# intc	        Identical to C int (normally int32 or int64)
# intp	        Integer used for indexing
# int8	        Byte (-128 to 127)
# int16	        Integer (-32768 to 32767)
# int32	            (-2147483648 to 2147483647)
# int64	            (-9223372036854775808 to 9223372036854775807)
# uint8	        Unsigned integer (0 to 255)
# uint16	        (0 to 65535)
# uint32	        (0 to 4294967295)
# uint64	        (0 to 18446744073709551615)
# float_	        Shorthand for float64.
# float16	        Half precision float: sign bit, 5 bits exponent, 10 bits
#                       mantissa
# float32	        Single precision float: sign bit, 8 bits exponent, 23 bits
#                       mantissa
# float64	        Double precision float: sign bit, 11 bits exponent, 52 bits
#                           mantissa
# complex_	    Shorthand for complex128.
# complex64	    Complex number, represented by two 32-bit floats
# complex128	    represented by two 64-bit floats
#
# This table was taken from the scipy.org website.
