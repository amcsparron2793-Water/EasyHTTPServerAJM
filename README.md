# <u>EasyHTTPServerAJM</u>
### <i>quick and dirty http server</i>



## To Add A New Validation Type:
______________________________
<span style="font-size: 12pt;">

1. Add an enum member to PathValidationType.

2. Extend resolve() so that, when appropriate, it sets self.is_resolved_to_<name> for that new type.

3. Use PathValidationType.<NAME> anywhere you create path+type tuples.

</span>


<span style="font-size: 11pt;">
Everything else ("\_resolved_flags", dynamic  
" is_resolved_to_* " attributes, and "validate()") is already generic and will just work.
</span>